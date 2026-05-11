-- Migrate any existing file-backed policies into the documents table
INSERT INTO public.documents (id, title, category, file_name, file_url, locations, created_at)
SELECT id, title, category, file_name, file_url, locations, created_at
FROM public.policies
WHERE file_name IS NOT NULL AND file_url IS NOT NULL
ON CONFLICT (id) DO NOTHING;

-- Reclassify policy chunks as documents
UPDATE public.chunks SET source_type = 'document' WHERE source_type = 'policy';

-- Narrow the check constraint to only allow 'document'
ALTER TABLE public.chunks DROP CONSTRAINT IF EXISTS chunks_source_type_check;
ALTER TABLE public.chunks ADD CONSTRAINT chunks_source_type_check
  CHECK (source_type IN ('document'));

-- Drop policies table
DROP TABLE IF EXISTS public.policies;
