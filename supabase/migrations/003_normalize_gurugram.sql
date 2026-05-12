-- Normalize location spelling: Gurgaon -> Gurugram
UPDATE public.profiles SET location = 'Gurugram' WHERE location = 'Gurgaon';
UPDATE public.chunks SET locations = array_replace(locations, 'Gurgaon', 'Gurugram') WHERE 'Gurgaon' = ANY(locations);
