"use client";
import "./creator.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { getMySubmissions } from "@/lib/api/content";
import { CreateModal } from "@/components/creator/CreateModal";
import { SubmissionRow } from "@/components/creator/SubmissionRow";

export default function CreatorPage() {
  const [showCreate, setShowCreate] = useState(false);

  const { data: submissions = [], isLoading } = useQuery({
    queryKey: ["content", "mine"],
    queryFn: () => getMySubmissions(),
  });

  return (
    <div className="page">
      <div className="creator-header page-header">
        <h1 className="page-title font-mono">Content Creator</h1>
        <button className="g-btn g-btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={14} />
          New Draft
        </button>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm mt-4">Loading…</div>
      ) : submissions.length === 0 ? (
        <div className="creator-empty">
          No submissions yet. Create a draft to get started.
        </div>
      ) : (
        <div className="creator-table-wrap">
          <table className="g-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub) => (
                <SubmissionRow key={sub.id} sub={sub} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && <CreateModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
