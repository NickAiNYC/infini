import type { Metadata } from "next";
import { Geist_Mono, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "INFINI Observatory — Open Standard for Agent Portability",
  description:
    "The declarative portability layer for AI agents. Write your logic once; execute it on any framework. Visualize execution traces in 3D.",
  keywords: [
    "INFINI",
    "Loopfile",
    "agent portability",
    "agent loops",
    "AI agents",
    "LangGraph",
    "CrewAI",
    "OpenAI Agents",
    "observatory",
    "trace visualization",
  ],
  authors: [{ name: "NickAiNYC and INFINI contributors" }],
  openGraph: {
    title: "INFINI Observatory",
    description: "The Open Standard for Agent Portability",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body
        className={`${plusJakarta.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
