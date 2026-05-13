-- Update chunks table to use 512-dimensional vectors (voyage-3 free tier)
alter table public.chunks
alter column embedding set data type vector(512) using embedding::vector(512);

-- Rebuild the IVFFlat index with new dimensions
drop index if exists public.chunks_embedding_idx;
create index chunks_embedding_idx on public.chunks
  using ivfflat (embedding vector_cosine_ops) with (lists = 100);
