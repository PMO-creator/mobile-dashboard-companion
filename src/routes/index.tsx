import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from "react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "MAZ 2026 — Dashboard Mobile (preview)" },
      {
        name: "description",
        content:
          "Preview do mobile.html do Dashboard MAZ 2026 (Museu das Amazônias).",
      },
    ],
  }),
  component: Index,
});

function Index() {
  useEffect(() => {
    // Auto-redirect the preview iframe to the static mobile.html served from /public
    window.location.replace("/mobile.html");
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#EEF3E8] p-6 text-[#1E293B]">
      <h1 className="text-lg font-bold">Preview: mobile.html</h1>
      <p className="text-sm text-[#64748B]">Abrindo o dashboard mobile…</p>
      <a
        href="/mobile.html"
        className="rounded-md bg-[#1E2E0D] px-4 py-2 text-sm font-semibold text-[#B8E85C]"
      >
        Abrir mobile.html
      </a>
    </div>
  );
}
