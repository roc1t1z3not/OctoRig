"use client";
import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bold, Italic, Heading2, Code, CodeSquare, Link, List, ListOrdered, Quote } from "lucide-react";

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: number;
  disabled?: boolean;
}

function insertWrap(
  el: HTMLTextAreaElement,
  setValue: (v: string) => void,
  prefix: string,
  suffix: string,
  fallback: string,
) {
  const { selectionStart: s, selectionEnd: e, value } = el;
  const selected = value.slice(s, e) || fallback;
  const next = value.slice(0, s) + prefix + selected + suffix + value.slice(e);
  setValue(next);
  requestAnimationFrame(() => {
    el.focus();
    el.setSelectionRange(s + prefix.length, s + prefix.length + selected.length);
  });
}

function insertPrefix(
  el: HTMLTextAreaElement,
  setValue: (v: string) => void,
  prefix: string,
) {
  const { selectionStart: s, value } = el;
  const lineStart = value.lastIndexOf("\n", s - 1) + 1;
  const next = value.slice(0, lineStart) + prefix + value.slice(lineStart);
  setValue(next);
  requestAnimationFrame(() => {
    el.focus();
    el.setSelectionRange(s + prefix.length, s + prefix.length);
  });
}

export function MarkdownEditor({
  value,
  onChange,
  placeholder = "Write markdown…",
  minHeight = 160,
  disabled = false,
}: MarkdownEditorProps) {
  const [tab, setTab] = useState<"write" | "preview">("write");
  const ref = useRef<HTMLTextAreaElement>(null);

  const wrap = (pre: string, suf: string, fallback: string) =>
    ref.current && insertWrap(ref.current, onChange, pre, suf, fallback);
  const pfx = (str: string) =>
    ref.current && insertPrefix(ref.current, onChange, str);

  const tools = [
    { icon: <Bold size={13} />,         title: "Bold",          action: () => wrap("**", "**", "bold text") },
    { icon: <Italic size={13} />,       title: "Italic",        action: () => wrap("*", "*", "italic text") },
    { icon: <Heading2 size={13} />,     title: "Heading",       action: () => pfx("## ") },
    { icon: <Code size={13} />,         title: "Inline code",   action: () => wrap("`", "`", "code") },
    { icon: <CodeSquare size={13} />,   title: "Code block",    action: () => wrap("```\n", "\n```", "code") },
    { icon: <Link size={13} />,         title: "Link",          action: () => wrap("[", "](url)", "link text") },
    { icon: <List size={13} />,         title: "Bullet list",   action: () => pfx("- ") },
    { icon: <ListOrdered size={13} />,  title: "Ordered list",  action: () => pfx("1. ") },
    { icon: <Quote size={13} />,        title: "Blockquote",    action: () => pfx("> ") },
  ];

  return (
    <div className="md-editor">
      <div className="md-editor-bar">
        <div className="md-editor-tabs">
          <button
            type="button"
            className={`g-btn g-btn-sm ${tab === "write" ? "g-btn-primary" : "g-btn-ghost"}`}
            onClick={() => setTab("write")}
          >
            Write
          </button>
          <button
            type="button"
            className={`g-btn g-btn-sm ${tab === "preview" ? "g-btn-primary" : "g-btn-ghost"}`}
            onClick={() => setTab("preview")}
          >
            Preview
          </button>
        </div>
        {tab === "write" && (
          <div className="md-editor-toolbar">
            {tools.map((t) => (
              <button
                key={t.title}
                type="button"
                className="md-toolbar-btn"
                title={t.title}
                disabled={disabled}
                onClick={t.action}
              >
                {t.icon}
              </button>
            ))}
          </div>
        )}
      </div>

      {tab === "write" ? (
        <textarea
          ref={ref}
          className="g-input md-editor-textarea"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          style={{ minHeight, resize: "vertical", fontFamily: "var(--font-mono, monospace)", fontSize: "0.8125rem" }}
          spellCheck={false}
        />
      ) : (
        <div className="md-preview" style={{ minHeight }}>
          {value ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
          ) : (
            <p className="md-preview-empty">Nothing to preview.</p>
          )}
        </div>
      )}
    </div>
  );
}
