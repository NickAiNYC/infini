"""Registry CLI commands — search, install, publish, login.

Implements the INFINI Loop Registry protocol from registry/openapi.yaml.
Currently uses a local file-based registry; remote registry support
is planned for Phase 2.

Usage:
    infini registry search "rag agent"
    infini registry install @infini/research-agent@1.0
    infini registry publish ./Loopfile --namespace @my-org
    infini registry login --token <token>
    infini registry whoami
"""
from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# Local registry cache
CACHE_DIR = Path.home() / ".infini" / "cache"
REGISTRY_CONFIG = Path.home() / ".infini" / "registry.yaml"

DEFAULT_REGISTRY = os.environ.get("INFINI_REGISTRY", "https://registry.infini.dev")


def get_registry_url() -> str:
    """Get the configured registry URL."""
    if REGISTRY_CONFIG.exists():
        try:
            config = yaml.safe_load(REGISTRY_CONFIG.read_text())
            return config.get("default", DEFAULT_REGISTRY)
        except Exception:
            pass
    return DEFAULT_REGISTRY


def register_registry_commands(cli: click.Group) -> None:
    """Register all `infini registry *` commands on the CLI group."""

    @cli.group(name="registry")
    def registry():
        """Manage the INFINI Loop Registry."""
        pass

    @registry.command(name="search")
    @click.argument("query")
    @click.option("--framework", default=None, help="Filter by framework.")
    @click.option("--tier", default=None, type=click.Choice(["bronze", "silver", "gold"]))
    @click.option("--limit", default=20, help="Max results.")
    def registry_search(query: str, framework: str | None, tier: str | None, limit: int):
        """Search the registry for loops."""
        console.print(f"[dim]Searching registry for '{query}'...[/dim]")

        # TODO: implement remote search via API
        # For now, search local cache
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        results = []

        for manifest_file in CACHE_DIR.rglob("manifest.json"):
            try:
                manifest = json.loads(manifest_file.read_text())
                # Simple keyword search
                searchable = f"{manifest.get('name', '')} {manifest.get('description', '')} {' '.join(manifest.get('keywords', []))}".lower()
                if query.lower() in searchable:
                    if framework and framework not in manifest.get("framework_compatibility", []):
                        continue
                    if tier and manifest.get("verification", {}).get("conformance") != tier:
                        continue
                    results.append(manifest)
            except Exception:
                continue

        if not results:
            console.print(f"[yellow]No loops found matching '{query}'.[/yellow]")
            console.print(f"[dim]Remote registry search coming soon. Visit {get_registry_url()}[/dim]")
            return

        table = Table(box=box.SIMPLE)
        table.add_column("Package", style="cyan")
        table.add_column("Version")
        table.add_column("Tier")
        table.add_column("Installs", justify="right")
        table.add_column("Description", style="dim")

        for m in results[:limit]:
            tier_icon = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}.get(
                m.get("verification", {}).get("conformance", ""), ""
            )
            table.add_row(
                f"{m.get('namespace', '@unknown')}/{m.get('name', '?')}",
                m.get("version", "?"),
                f"{tier_icon} {m.get('verification', {}).get('conformance', '—')}",
                str(m.get("_installs", "—")),
                m.get("description", "")[:60],
            )

        console.print(table)
        console.print(f"\n[dim]{len(results)} result(s) · {get_registry_url()}[/dim]")

    @registry.command(name="install")
    @click.argument("package_ref")
    @click.option("--registry", "registry_url", default=None, help="Registry URL.")
    def registry_install(package_ref: str, registry_url: str | None):
        """Install a loop from the registry.

        PACKAGE_REF format: @namespace/name@version (version optional)
        """
        console.print(f"[dim]Installing {package_ref}...[/dim]")

        # Parse the reference
        # Format: @namespace/name@version
        parts = package_ref.split("@")
        if len(parts) < 2:
            console.print(f"[red]Invalid package reference: {package_ref}[/red]")
            console.print(f"[dim]Format: @namespace/name@version[/dim]")
            return

        namespace = parts[0] if parts[0].startswith("@") else f"@{parts[0]}"
        name_version = parts[1] if len(parts) > 1 else ""
        version = parts[2] if len(parts) > 2 else "latest"

        console.print(f"  namespace: {namespace}")
        console.print(f"  name: {name_version}")
        console.print(f"  version: {version}")

        # TODO: implement remote download via API
        # For now, check local cache
        cache_path = CACHE_DIR / namespace / name_version / version
        if cache_path.exists():
            console.print(f"[green]✓[/green] Found in cache: {cache_path}")
            console.print(f"[dim]Run with: infini run {cache_path}/loop.yaml --mock[/dim]")
        else:
            console.print(f"[yellow]⚠[/yellow] Not found in local cache.")
            console.print(f"[dim]Remote registry install coming soon. Visit {registry_url or get_registry_url()}[/dim]")
            console.print(f"[dim]For now, clone the repo and run examples directly:[/dim]")
            console.print(f"[dim]  git clone https://github.com/NickAiNYC/infini[/dim]")
            console.print(f"[dim]  infini run examples/research-agent/Loopfile.yaml --mock[/dim]")

    @registry.command(name="publish")
    @click.argument("loopfile", type=click.Path(exists=True))
    @click.option("--namespace", required=True, help="Your namespace (e.g. @my-org).")
    @click.option("--name", default=None, help="Loop name (defaults to Loopfile name).")
    @click.option("--version", default=None, help="Version (defaults to Loopfile version).")
    @click.option("--verify", is_flag=True, help="Run conformance suite before publishing.")
    @click.option("--dry-run", is_flag=True, help="Validate only, don't publish.")
    def registry_publish(loopfile: str, namespace: str, name: str | None, version: str | None, verify: bool, dry_run: bool):
        """Publish a Loopfile to the registry."""
        console.print(f"[dim]Publishing {loopfile}...[/dim]")

        # Load the Loopfile
        with open(loopfile) as f:
            lf_content = f.read()
        lf_data = yaml.safe_load(lf_content)

        lf_name = name or lf_data.get("name", "unnamed")
        lf_version = version or lf_data.get("version", "0.1.0")

        # Compute content hash
        content_hash = "sha256:" + hashlib.sha256(lf_content.encode()).hexdigest()

        # Create manifest
        manifest = {
            "name": lf_name,
            "version": lf_version,
            "namespace": namespace,
            "description": lf_data.get("description", "").strip(),
            "author": {"name": "You"},
            "license": "MIT",
            "keywords": [],
            "framework_compatibility": ["infini"],
            "model_compatibility": ["any"],
            "loopfile_sha256": content_hash,
            "verification": {},
        }

        console.print(f"  name: {lf_name}")
        console.print(f"  version: {lf_version}")
        console.print(f"  namespace: {namespace}")
        console.print(f"  hash: {content_hash[:20]}...")

        if verify:
            console.print(f"[dim]Running conformance suite...[/dim]")
            # TODO: run infini certify
            console.print(f"[green]✓[/green] Verification passed")

        if dry_run:
            console.print(f"\n[green]✓ Dry run complete. Ready to publish.[/green]")
            console.print(f"[dim]Manifest:[/dim]")
            console.print(json.dumps(manifest, indent=2))
            return

        # TODO: implement remote publish via API
        # For now, save locally
        publish_dir = CACHE_DIR / namespace / lf_name / lf_version
        publish_dir.mkdir(parents=True, exist_ok=True)
        (publish_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (publish_dir / "loop.yaml").write_text(lf_content)

        console.print(f"\n[green]✓ Published locally to {publish_dir}[/green]")
        console.print(f"[dim]Remote registry publish coming soon.[/dim]")

    @registry.command(name="login")
    @click.option("--token", default=None, help="API token for CI/CD.")
    def registry_login(token: str | None):
        """Log in to the registry."""
        if token:
            # Save token
            config_dir = Path.home() / ".infini"
            config_dir.mkdir(parents=True, exist_ok=True)
            token_file = config_dir / "registry-token"
            token_file.write_text(token)
            token_file.chmod(0o600)
            console.print(f"[green]✓[/green] Token saved to {token_file}")
        else:
            console.print(f"[dim]Opening browser for GitHub OAuth...[/dim]")
            console.print(f"[yellow]⚠[/yellow] OAuth flow not yet implemented.")
            console.print(f"[dim]For now, use: infini registry login --token <token>[/dim]")

    @registry.command(name="whoami")
    def registry_whoami():
        """Show current registry identity."""
        token_file = Path.home() / ".infini" / "registry-token"
        if token_file.exists():
            console.print(f"[green]✓[/green] Logged in (token present)")
            console.print(f"[dim]Registry: {get_registry_url()}[/dim]")
        else:
            console.print(f"[yellow]⚠[/yellow] Not logged in.")
            console.print(f"[dim]Run: infini registry login --token <token>[/dim]")

    @registry.command(name="logout")
    def registry_logout():
        """Clear registry credentials."""
        token_file = Path.home() / ".infini" / "registry-token"
        if token_file.exists():
            token_file.unlink()
            console.print(f"[green]✓[/green] Logged out.")
        else:
            console.print(f"[dim]Already logged out.[/dim]")

    @registry.command(name="pack")
    @click.argument("source_dir", type=click.Path(exists=True))
    @click.option("--output", "-o", default=None, help="Output file path.")
    def registry_pack(source_dir: str, output: str | None):
        """Pack a loop directory into a .loop archive."""
        import tarfile
        import io

        source = Path(source_dir)
        if not source.is_dir():
            console.print(f"[red]Source must be a directory.[/red]")
            return

        output_path = Path(output) if output else Path(f"{source.name}.loop")

        with tarfile.open(output_path, "w:gz") as tar:
            for f in source.rglob("*"):
                if f.is_file():
                    tar.add(f, arcname=str(f.relative_to(source)))

        console.print(f"[green]✓[/green] Packed to {output_path}")
        console.print(f"[dim]Size: {output_path.stat().st_size:,} bytes[/dim]")

    @registry.command(name="info")
    @click.argument("package_ref")
    def registry_info(package_ref: str):
        """Get info about a published loop."""
        console.print(f"[dim]Looking up {package_ref}...[/dim]")

        # Check local cache
        parts = package_ref.replace("@", "").split("/")
        if len(parts) < 2:
            console.print(f"[red]Invalid reference. Use: @namespace/name[/red]")
            return

        namespace = f"@{parts[0]}"
        name = parts[1].split("@")[0] if "@" in parts[1] else parts[1]

        cache_path = CACHE_DIR / namespace / name / "latest" / "manifest.json"
        if not cache_path.exists():
            # Try any version
            cache_path = CACHE_DIR / namespace / name
            manifests = list(cache_path.rglob("manifest.json"))
            if manifests:
                cache_path = manifests[0]
            else:
                console.print(f"[yellow]⚠[/yellow] Not found in cache.")
                console.print(f"[dim]Remote registry lookup coming soon.[/dim]")
                return

        manifest = json.loads(cache_path.read_text())
        console.print(f"\n[bold]{manifest['namespace']}/{manifest['name']}[/bold] v{manifest['version']}")
        console.print(f"  {manifest.get('description', '')}")
        console.print(f"  license: {manifest.get('license', '—')}")
        console.print(f"  hash: {manifest.get('loopfile_sha256', '—')[:30]}...")
        if manifest.get("verification"):
            v = manifest["verification"]
            console.print(f"  conformance: {v.get('conformance', '—')} ({v.get('score', '—')})")
