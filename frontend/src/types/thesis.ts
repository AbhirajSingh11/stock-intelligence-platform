export type ThesisStatus = "DRAFT" | "ACTIVE" | "INVALIDATED" | "ARCHIVED";
export type ThesisConviction = "LOW" | "MEDIUM" | "HIGH";
export type ThesisSignal = "STRENGTHENING" | "STABLE" | "WEAKENING" | "REVIEW_REQUIRED";
export type EvidenceStance = "SUPPORTING" | "CONTRADICTING" | "NEUTRAL";
export type EvidenceCategory =
  | "FINANCIAL"
  | "COMPETITIVE"
  | "MANAGEMENT"
  | "VALUATION"
  | "CATALYST"
  | "RISK"
  | "FILING"
  | "OTHER";

export interface EvidenceCounts {
  supporting: number;
  contradicting: number;
  neutral: number;
  total: number;
}

export interface ThesisSummary {
  id: number;
  ticker: string;
  cik: string;
  company_name: string;
  title: string;
  summary: string;
  status: ThesisStatus;
  conviction: ThesisConviction;
  signal: ThesisSignal;
  review_due_date: string | null;
  last_reviewed_at: string | null;
  created_at: string;
  updated_at: string;
  is_overdue: boolean;
  evidence_counts: EvidenceCounts;
}

export interface ThesisEvidence {
  id: number;
  thesis_id: number;
  stance: EvidenceStance;
  category: EvidenceCategory;
  title: string;
  description: string;
  source_url: string | null;
  observed_on: string;
  created_at: string;
  updated_at: string;
}

export interface ThesisDetail extends ThesisSummary {
  bull_case: string | null;
  bear_case: string | null;
  invalidation_criteria: string | null;
  evidence: ThesisEvidence[];
}

export interface ThesisJournalCounts {
  total: number;
  active: number;
  overdue: number;
  review_required: number;
}

export interface ThesisListResponse {
  theses: ThesisSummary[];
  counts: ThesisJournalCounts;
}

export interface ThesisFieldsInput {
  title: string;
  summary: string;
  bull_case: string | null;
  bear_case: string | null;
  invalidation_criteria: string | null;
  status: ThesisStatus;
  conviction: ThesisConviction;
  signal: ThesisSignal;
  review_due_date: string | null;
}

export interface ThesisCreateInput extends ThesisFieldsInput {
  ticker: string;
}

export type ThesisUpdateInput = Partial<ThesisFieldsInput>;

export interface EvidenceInput {
  stance: EvidenceStance;
  category: EvidenceCategory;
  title: string;
  description: string;
  source_url: string | null;
  observed_on: string;
}

export type EvidenceUpdateInput = Partial<EvidenceInput>;

export interface ThesisDeleteResponse {
  ticker: string;
  deleted: true;
}

export interface EvidenceDeleteResponse {
  evidence_id: number;
  deleted: true;
}
