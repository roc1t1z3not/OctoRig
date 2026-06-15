export function RankNum({ n }: { n: number }) {
  if (n === 1) return <span className="sb-rank-num sb-rank-num--gold"><span className="sb-medal">🥇</span>1</span>;
  if (n === 2) return <span className="sb-rank-num sb-rank-num--silver"><span className="sb-medal">🥈</span>2</span>;
  if (n === 3) return <span className="sb-rank-num sb-rank-num--bronze"><span className="sb-medal">🥉</span>3</span>;
  return <span className="sb-rank-num">{n}</span>;
}
