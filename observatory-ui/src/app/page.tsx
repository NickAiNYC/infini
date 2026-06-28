"use client";

import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import {
  type LucideIcon,
  Shield,
  Lock,
  RefreshCw,
  Search,
  Activity,
  Clock,
  CheckCircle2,
  Boxes,
  Upload,
  Cpu,
  Zap,
  AlertTriangle,
  FileJson,
  Play,
  ChevronRight,
} from "lucide-react";

// ────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────
interface StepTrace {
  id: string;
  name: string;
  status: string;
  started_at: string;
  ended_at: string;
  cost: { dollars: number; minutes: number; tokens: { input: number; output: number; total: number } };
  artifacts: string[];
  agent: string;
  action: string;
  retry_attempt: number | null;
}

interface CheckResult {
  check: string;
  status: string;
  confidence: number | null;
  detail: string | null;
}

interface Trace {
  loopfile: string;
  loopfile_hash: string;
  engine: { type: string; version: string };
  started_at: string;
  ended_at: string | null;
  iterations: number;
  steps: StepTrace[];
  verifications: CheckResult[];
  budget: { spent_dollars: number; spent_minutes: number };
  outcome: string;
  lessons: string[];
  provenance: Record<string, unknown>;
  replay_of?: string | null;
  replay_from_step?: string | null;
}

// ────────────────────────────────────────────────────────────
// Sample trace (used before user uploads one)
// ────────────────────────────────────────────────────────────
const SAMPLE_TRACE: Trace = {
  loopfile: "infini/governed-coding-loop@1.0.0",
  loopfile_hash: "sha256:b7c1f3a2e9d8c7b6a5e4f3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2",
  engine: { type: "hermes + openclaw", version: "1.0.0" },
  started_at: "2026-06-28T10:42:50Z",
  ended_at: "2026-06-28T10:47:11Z",
  iterations: 2,
  steps: [
    { id: "s1", name: "plan", status: "ok", started_at: "2026-06-28T10:42:50Z", ended_at: "2026-06-28T10:43:32Z", cost: { dollars: 0.18, minutes: 0.7, tokens: { input: 2100, output: 800, total: 2900 } }, artifacts: ["plan.md"], agent: "planner", action: "coding.plan", retry_attempt: null },
    { id: "s2", name: "policy_check", status: "ok", started_at: "2026-06-28T10:43:32Z", ended_at: "2026-06-28T10:44:26Z", cost: { dollars: 0.31, minutes: 0.9, tokens: { input: 3200, output: 1100, total: 4300 } }, artifacts: ["policy_check.json"], agent: "auditor", action: "policy.cross_check", retry_attempt: null },
    { id: "s3", name: "audit_pre", status: "ok", started_at: "2026-06-28T10:44:26Z", ended_at: "2026-06-28T10:44:44Z", cost: { dollars: 0.12, minutes: 0.3, tokens: { input: 800, output: 400, total: 1200 } }, artifacts: ["audit/pre.jsonl"], agent: "auditor", action: "audit.sign", retry_attempt: null },
    { id: "s4", name: "edit_files", status: "ok", started_at: "2026-06-28T10:44:44Z", ended_at: "2026-06-28T10:45:56Z", cost: { dollars: 0.34, minutes: 1.2, tokens: { input: 2800, output: 1400, total: 4200 } }, artifacts: ["src/dark-mode.tsx", "src/dark-mode.css"], agent: "coder", action: "file_system.write", retry_attempt: null },
    { id: "s5", name: "run_tests", status: "ok", started_at: "2026-06-28T10:45:56Z", ended_at: "2026-06-28T10:46:44Z", cost: { dollars: 0.21, minutes: 0.8, tokens: { input: 1500, output: 600, total: 2100 } }, artifacts: ["test-output.log"], agent: "tester", action: "terminal.run", retry_attempt: 1 },
    { id: "s6", name: "open_pr", status: "ok", started_at: "2026-06-28T10:46:44Z", ended_at: "2026-06-28T10:47:20Z", cost: { dollars: 0.22, minutes: 0.6, tokens: { input: 1200, output: 500, total: 1700 } }, artifacts: ["pr-url.txt"], agent: "coder", action: "github.open_pr", retry_attempt: null },
    { id: "s7", name: "audit_post", status: "ok", started_at: "2026-06-28T10:47:20Z", ended_at: "2026-06-28T10:47:41Z", cost: { dollars: 0.14, minutes: 0.35, tokens: { input: 900, output: 400, total: 1300 } }, artifacts: ["audit/post.jsonl"], agent: "auditor", action: "audit.sign", retry_attempt: null },
    { id: "s8", name: "verify_governed", status: "ok", started_at: "2026-06-28T10:47:11Z", ended_at: "2026-06-28T10:47:41Z", cost: { dollars: 0.18, minutes: 0.5, tokens: { input: 1800, output: 700, total: 2500 } }, artifacts: ["governance-verify.json"], agent: "auditor", action: "governance.verify", retry_attempt: null },
  ],
  verifications: [
    { check: "plan.md:exists", status: "pass", confidence: null, detail: null },
    { check: "policy_check.json:status_pass", status: "pass", confidence: null, detail: null },
    { check: "audit/post.jsonl:non_empty", status: "pass", confidence: null, detail: "12 lines" },
    { check: "test-output.log:exit_zero", status: "pass", confidence: null, detail: "exit 0" },
    { check: "pr-url.txt:valid_url", status: "pass", confidence: null, detail: "PR #4130" },
    { check: "judge:policy_citation>=90", status: "pass", confidence: 95, detail: null },
    { check: "judge:feature_completeness>=90", status: "pass", confidence: 92, detail: null },
    { check: "judge:test_coverage>=85", status: "pass", confidence: 87, detail: null },
  ],
  budget: { spent_dollars: 1.7, spent_minutes: 4.35 },
  outcome: "verified",
  lessons: ["Dark-mode toggle implemented in 4 minutes. Start from src/App.tsx in future runs."],
  provenance: { engine_signature: "ed25519:2b4f..." },
};

// ────────────────────────────────────────────────────────────
// 3D Galaxy Globe (React Three Fiber)
// ────────────────────────────────────────────────────────────
function GalaxyStepNode({
  position,
  stepId,
  status,
  isHighlighted,
  onClick,
}: {
  position: THREE.Vector3;
  stepId: string;
  status: string;
  isHighlighted: boolean;
  onClick: () => void;
}) {
  const color = status === "ok" ? "#06b6d4" : status === "failed" ? "#ef4444" : "#f59e0b";

  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onClick(); }}>
      <mesh>
        <sphereGeometry args={[isHighlighted ? 0.16 : 0.11, 24, 24]} />
        <meshBasicMaterial color={color} transparent opacity={isHighlighted ? 0.95 : 0.78} />
      </mesh>
      <mesh>
        <sphereGeometry args={[isHighlighted ? 0.34 : 0.25, 24, 24]} />
        <meshBasicMaterial color={color} transparent opacity={isHighlighted ? 0.18 : 0.09} />
      </mesh>
      <sprite scale={[0.46, 0.16, 1]} position={[0, 0.28, 0]}>
        <spriteMaterial color={color} transparent opacity={isHighlighted ? 0.55 : 0.22} />
      </sprite>
    </group>
  );
}

function GalaxyStars({ count = 420 }: { count?: number }) {
  const { positions, colors } = useMemo(() => {
    const positionArray = new Float32Array(count * 3);
    const colorArray = new Float32Array(count * 3);
    const palette = [
      new THREE.Color("#7c5cff"),
      new THREE.Color("#4ea8ff"),
      new THREE.Color("#3ecf8e"),
      new THREE.Color("#e6e8ee"),
    ];

    for (let i = 0; i < count; i += 1) {
      const radius = 1.65 + ((i * 17) % 100) / 100 * 0.55;
      const theta = i * 2.399963229728653;
      const y = 1 - (i / (count - 1)) * 2;
      const ring = Math.sqrt(1 - y * y);
      const arm = Math.sin(i * 0.13) * 0.14;

      positionArray[i * 3] = Math.cos(theta) * ring * radius + arm;
      positionArray[i * 3 + 1] = y * radius;
      positionArray[i * 3 + 2] = Math.sin(theta) * ring * radius;

      const color = palette[i % palette.length];
      colorArray[i * 3] = color.r;
      colorArray[i * 3 + 1] = color.g;
      colorArray[i * 3 + 2] = color.b;
    }

    return { positions: positionArray, colors: colorArray };
  }, [count]);

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.025} vertexColors transparent opacity={0.82} sizeAttenuation depthWrite={false} />
    </points>
  );
}

function TraceGlobe3D({
  trace,
  selectedStep,
  onSelectStep,
}: {
  trace: Trace;
  selectedStep: string | null;
  onSelectStep: (id: string) => void;
}) {
  return (
    <Canvas camera={{ position: [0, 0.8, 7], fov: 46 }}>
      <GalaxyScene trace={trace} selectedStep={selectedStep} onSelectStep={onSelectStep} />
    </Canvas>
  );
}

function GalaxyScene({
  trace,
  selectedStep,
  onSelectStep,
}: {
  trace: Trace;
  selectedStep: string | null;
  onSelectStep: (id: string) => void;
}) {
  const galaxyRef = useRef<THREE.Group>(null);
  const haloRef = useRef<THREE.Mesh>(null);
  const steps = trace.steps;

  const nodePositions = useMemo(() => {
    const radius = 2.35;
    return steps.map((_, i) => {
      const t = steps.length === 1 ? 0.5 : i / (steps.length - 1);
      const y = 1 - t * 2;
      const ring = Math.sqrt(1 - y * y);
      const theta = i * 2.399963229728653 + 0.7;
      return new THREE.Vector3(
        Math.cos(theta) * ring * radius,
        y * radius,
        Math.sin(theta) * ring * radius
      );
    });
  }, [steps]);

  useFrame((_, delta) => {
    if (galaxyRef.current) galaxyRef.current.rotation.y += delta * 0.08;
    if (haloRef.current) haloRef.current.rotation.z += delta * 0.05;
  });

  return (
    <>
      <color attach="background" args={["#0b0d12"]} />
      <ambientLight intensity={0.18} />
      <pointLight position={[4, 3, 5]} intensity={1.1} color="#4ea8ff" />
      <pointLight position={[-5, -2, -2]} intensity={0.8} color="#7c5cff" />

      <group ref={galaxyRef} rotation={[0.22, 0, -0.12]}>
        <GalaxyStars />
        <mesh ref={haloRef}>
          <sphereGeometry args={[2.22, 64, 64]} />
          <meshBasicMaterial color="#4ea8ff" wireframe transparent opacity={0.055} />
        </mesh>
        <mesh rotation={[Math.PI / 2.3, 0, 0]}>
          <torusGeometry args={[2.55, 0.012, 12, 160]} />
          <meshBasicMaterial color="#7c5cff" transparent opacity={0.42} />
        </mesh>
        <mesh rotation={[Math.PI / 2.8, 0.2, 0.8]}>
          <torusGeometry args={[2.9, 0.008, 12, 160]} />
          <meshBasicMaterial color="#3ecf8e" transparent opacity={0.24} />
        </mesh>
        <mesh>
          <sphereGeometry args={[1.05, 48, 48]} />
          <meshBasicMaterial color="#11141b" transparent opacity={0.38} />
        </mesh>

        {steps.map((step, i) => (
          <GalaxyStepNode
            key={`${step.id}-${i}`}
            position={nodePositions[i]}
            stepId={step.id}
            status={step.status}
            isHighlighted={selectedStep === step.id}
            onClick={() => onSelectStep(step.id)}
          />
        ))}
      </group>

      <OrbitControls
        enablePan={false}
        minDistance={4.5}
        maxDistance={11}
        autoRotate
        autoRotateSpeed={0.28}
      />
    </>
  );
}

// ────────────────────────────────────────────────────────────
// Stat Card
// ────────────────────────────────────────────────────────────
function StatCard({
  label,
  value,
  status,
  statusType,
  icon: Icon,
  delay,
}: {
  label: string;
  value: string;
  status: string;
  statusType: "cyan" | "green" | "muted";
  icon: LucideIcon;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className="glow-card p-4"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="label-caps flex items-center gap-2">
          <Icon className="w-3 h-3" />
          {label}
        </div>
        <span className={`chip chip-${statusType}`}>{status}</span>
      </div>
      <div
        className={`text-[1.35rem] font-semibold tracking-normal ${
          statusType === "green" ? "text-glow-green" : "text-white"
        }`}
      >
        {value}
      </div>
    </motion.div>
  );
}

// ────────────────────────────────────────────────────────────
// Tab Bar
// ────────────────────────────────────────────────────────────
const TABS = ["LIVE AGENT LOGS", "TRACE REPLAYS", "ERROR ANALYSIS", "DEPLOYED LOOPS"] as const;

// ────────────────────────────────────────────────────────────
// Main Page
// ────────────────────────────────────────────────────────────
export default function ObservatoryPage() {
  const [trace, setTrace] = useState<Trace>(SAMPLE_TRACE);
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>("LIVE AGENT LOGS");
  const [selectedStep, setSelectedStep] = useState<string | null>("s5");
  const [searchQuery, setSearchQuery] = useState("");
  const [particles, setParticles] = useState<
    Array<{ id: number; left: string; top: string; delay: string; duration: string }>
  >([]);
  const [mounted, setMounted] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Generate particles only on the client to avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
    setParticles(
      Array.from({ length: 12 }, (_, i) => ({
        id: i,
        left: `${(i * 37 + 13) % 100}%`,
        top: `${(i * 53 + 29) % 100}%`,
        delay: `${(i * 0.7) % 8}s`,
        duration: `${8 + (i % 6)}s`,
      }))
    );
  }, []);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target?.result as string) as Trace;
        if (parsed.loopfile && parsed.steps) {
          setTrace(parsed);
          setSelectedStep(null);
        }
      } catch {
        // Invalid JSON — keep current trace
      }
    };
    reader.readAsText(file);
  }, []);

  const selectedStepData = trace.steps.find(
    (s) => s.id === selectedStep
  );

  // Floating particles for atmosphere
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Atmospheric particles */}
      {particles.map((p) => (
        <div
          key={p.id}
          className="particle"
          style={{ left: p.left, top: p.top, animationDelay: p.delay, animationDuration: p.duration }}
        />
      ))}

      <div className="relative z-10 max-w-[1440px] mx-auto px-5 py-5">
        {/* ── Header ── */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="topbar-shell flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-4"
        >
          <div className="min-w-0">
            <div className="label-caps mb-2 flex items-center gap-2">
              <Boxes className="w-3 h-3" />
              OPEN STANDARD / AGENT PORTABILITY
            </div>
            <h1 className="text-[1.65rem] font-semibold tracking-normal text-white leading-tight">
              INFINI <span className="text-accent-violet">Observatory</span>
            </h1>
            <p className="text-xs text-muted-gem mt-1 max-w-2xl">
              The declarative portability layer for AI agents. Write your logic once;
              execute it on any framework. Visualize execution traces in 3D.
            </p>
          </div>
          <div className="grid w-full grid-cols-2 gap-2 sm:flex sm:w-auto sm:items-center">
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.trace"
              onChange={handleFileUpload}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn-ghost flex items-center justify-center gap-2 text-xs"
            >
              <Upload className="w-4 h-4" />
              Upload Trace
            </button>
            <button className="btn-cyan flex items-center justify-center gap-2 text-xs">
              <RefreshCw className="w-4 h-4" />
              Run Agent Loop
            </button>
          </div>
        </motion.header>

        {/* ── Stat Cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          <StatCard
            label="TOTAL AGENT RUNS"
            value="12,501"
            status="ACTIVE"
            statusType="cyan"
            icon={Activity}
            delay={0.1}
          />
          <StatCard
            label="ACTIVE SESSIONS"
            value="4"
            status="MONITORING"
            statusType="cyan"
            icon={Cpu}
            delay={0.2}
          />
          <StatCard
            label="MEAN REPLAY TIME"
            value="3.2s"
            status="CALCULATED"
            statusType="muted"
            icon={Clock}
            delay={0.3}
          />
          <StatCard
            label="CERTIFIED ADAPTERS"
            value="8"
            status="VERIFIED"
            statusType="green"
            icon={CheckCircle2}
            delay={0.4}
          />
        </div>

        {/* ── Tab Bar + Search ── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between mb-4 border-b border-gem pb-2"
        >
          <div className="flex w-full items-center gap-1 overflow-x-auto">
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium tracking-wide transition-colors ${
                  activeTab === tab
                    ? "tab-active"
                    : "text-muted-gem hover:text-slate-200"
                } whitespace-nowrap`}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="relative w-full lg:w-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400/60" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter logs by task, model..."
              className="bg-panel-gem border border-gem rounded-md pl-10 pr-4 py-2 text-xs text-slate-200 placeholder:text-gem-dim focus:outline-none focus:border-violet-400/60 transition-all w-full lg:w-72"
            />
          </div>
        </motion.div>

        {/* ── Main Content: 3D Trace + Replay Detail ── */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          {/* Left: 3D Trace Visualizer */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.6 }}
            className="lg:col-span-3 glow-card p-4 h-[560px] relative overflow-hidden"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Boxes className="w-4 h-4 text-accent-blue" />
                <h2 className="label-caps">GALAXY TRACE GLOBE</h2>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-muted-gem">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#06b6d4]" />
                  OK
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_8px_#f59e0b]" />
                  RETRIED
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-red-400 shadow-[0_0_8px_#ef4444]" />
                  FAILED
                </span>
              </div>
            </div>
            <div className="h-[466px] rounded-lg overflow-hidden border border-gem bg-[#0b0d12]">
              {mounted ? (
                <TraceGlobe3D
                  trace={trace}
                  selectedStep={selectedStep}
                  onSelectStep={setSelectedStep}
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="w-8 h-8 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
                </div>
              )}
            </div>
            <div className="absolute bottom-4 left-5 text-[11px] text-gem-dim font-mono">
              Drag to rotate / scroll to zoom / click a star node
            </div>
          </motion.div>

          {/* Right: Step Detail / Replay Visualization */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.7 }}
            className="lg:col-span-2 glow-card p-4 h-[560px] overflow-y-auto"
          >
            <div className="flex items-center gap-2 mb-4">
              <Lock className="w-4 h-4 text-accent-blue" />
              <h2 className="label-caps">AGENT REPLAY VISUALIZATION CENTER</h2>
            </div>

            {selectedStepData ? (
              <AnimatePresence mode="wait">
                <motion.div
                  key={selectedStepData.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Step header */}
                  <div className="mb-5">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-accent-blue">
                        {selectedStepData.id}
                      </span>
                      <ChevronRight className="w-3 h-3 text-gem-dim" />
                      <span className="text-lg font-semibold text-white">
                        {selectedStepData.name}
                      </span>
                    </div>
                    <div className="text-xs text-muted-gem font-mono">
                      {selectedStepData.action} · agent: {selectedStepData.agent}
                    </div>
                  </div>

                  {/* Status */}
                  <div className="mb-4 flex items-center gap-2">
                    {selectedStepData.status === "ok" ? (
                      <span className="chip chip-green">
                        <CheckCircle2 className="w-3 h-3" /> PASSED
                      </span>
                    ) : (
                      <span className="chip chip-cyan">
                        <AlertTriangle className="w-3 h-3" /> {selectedStepData.status.toUpperCase()}
                      </span>
                    )}
                    {selectedStepData.retry_attempt && (
                      <span className="chip chip-muted">RETRY {selectedStepData.retry_attempt}</span>
                    )}
                  </div>

                  {/* Cost breakdown */}
                  <div className="grid grid-cols-3 gap-2 mb-5">
                    <div className="bg-panel-gem rounded-lg p-3 border border-gem">
                      <div className="text-[10px] text-muted-gem uppercase tracking-wider mb-1">Cost</div>
                      <div className="text-lg font-semibold text-accent-blue">
                        ${selectedStepData.cost.dollars.toFixed(2)}
                      </div>
                    </div>
                    <div className="bg-panel-gem rounded-lg p-3 border border-gem">
                      <div className="text-[10px] text-muted-gem uppercase tracking-wider mb-1">Time</div>
                      <div className="text-lg font-semibold text-white">
                        {selectedStepData.cost.minutes.toFixed(1)}m
                      </div>
                    </div>
                    <div className="bg-panel-gem rounded-lg p-3 border border-gem">
                      <div className="text-[10px] text-muted-gem uppercase tracking-wider mb-1">Tokens</div>
                      <div className="text-lg font-semibold text-white">
                        {selectedStepData.cost.tokens.total.toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {/* Artifacts */}
                  <div className="mb-5">
                    <div className="label-caps mb-2 flex items-center gap-1.5">
                      <FileJson className="w-3 h-3" />
                      ARTIFACTS
                    </div>
                    <div className="space-y-1.5">
                      {selectedStepData.artifacts.map((a) => (
                        <div
                          key={a}
                          className="flex items-center gap-2 px-3 py-2 bg-panel-gem rounded-md border border-gem text-xs font-mono text-slate-300"
                        >
                          <FileJson className="w-3 h-3 text-accent-violet" />
                          {a}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Replay button */}
                  <button className="w-full btn-cyan flex items-center justify-center gap-2 text-sm">
                    <Play className="w-4 h-4" />
                    REPLAY FROM {selectedStepData.id.toUpperCase()}
                  </button>
                </motion.div>
              </AnimatePresence>
            ) : (
              <div className="flex flex-col items-center justify-center h-[420px] text-center">
                <div className="w-16 h-16 rounded-full bg-violet-500/10 flex items-center justify-center mb-4 pulse-cyan">
                  <Zap className="w-7 h-7 text-accent-violet" />
                </div>
                <div className="text-muted-gem text-sm mb-2">No Replay Selected</div>
                <div className="text-gem-dim text-xs max-w-xs">
                  Select any node in the 3D graph to visualize its execution steps,
                  cost accounting, and memory state.
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* ── Bottom: Log Stream + Verification ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
          {/* Log Stream */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="glow-card p-4 h-[300px] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-accent-blue" />
                <h2 className="label-caps">AUDITED AGENT LOOP LOG STREAM</h2>
              </div>
              <span className="chip chip-cyan">{trace.steps.length} ENTRIES</span>
            </div>
            <div className="space-y-1 font-mono text-xs">
              {trace.steps.map((s, i) => (
                <motion.div
                  key={`${s.id}-${i}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.9 + i * 0.05 }}
                  className={`flex items-center gap-3 px-3 py-2 rounded border-l-2 cursor-pointer transition-colors ${
                    selectedStep === s.id
                      ? "bg-violet-500/10 border-violet-400"
                      : "border-transparent hover:bg-panel-gem"
                  }`}
                  onClick={() => setSelectedStep(s.id)}
                >
                  <span className="text-gem-dim w-16">{s.started_at.split("T")[1]?.split("Z")[0]}</span>
                  <span className={`w-2 h-2 rounded-full ${s.status === "ok" ? "bg-cyan-400 shadow-[0_0_6px_#06b6d4]" : "bg-amber-400 shadow-[0_0_6px_#f59e0b]"}`} />
                  <span className="text-accent-blue w-8">{s.id}</span>
                  <span className="text-slate-300 flex-1">{s.name}</span>
                  <span className="text-muted-gem">${s.cost.dollars.toFixed(2)}</span>
                  <span className="text-gem-dim">{s.cost.minutes.toFixed(1)}m</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Verification Panel */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
            className="glow-card p-4 h-[300px] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <h2 className="label-caps">VERIFICATION RESULTS</h2>
              </div>
              <span className="chip chip-green">
                {trace.outcome.toUpperCase()}
              </span>
            </div>
            <div className="space-y-1.5">
              {trace.verifications.map((v, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.0 + i * 0.04 }}
                  className="flex items-center gap-3 px-3 py-2 rounded bg-panel-gem border border-gem"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span className="font-mono text-xs text-slate-300 flex-1 truncate">
                    {v.check}
                  </span>
                  {v.confidence !== null && (
                    <span className="text-xs font-mono text-accent-blue">
                      {v.confidence.toFixed(0)}
                    </span>
                  )}
                  <span className={`text-[10px] font-semibold uppercase tracking-wider ${
                    v.status === "pass" ? "text-emerald-400" : "text-red-400"
                  }`}>
                    {v.status}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* ── Footer ── */}
        <div className="mt-5 flex items-center justify-between text-xs text-gem-dim font-mono">
          <span>COMMAND CENTER</span>
          <span>
            INFINI v1.0.0 · LOOPFILE-1.0 ·{" "}
            <span className="text-accent-violet">infini.dev</span>
          </span>
        </div>
      </div>
    </div>
  );
}
