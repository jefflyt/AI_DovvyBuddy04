-- First, add columns that can be NULL
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "dive_site_id" text;
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "difficulty_rating" integer;
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "depth_min_m" real;
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "depth_max_m" real;
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "tags" json;
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "last_updated" timestamp with time zone;
ALTER TABLE "dive_sites" ADD COLUMN IF NOT EXISTS "updated_at" timestamp with time zone DEFAULT now();

-- Update existing records to have a dive_site_id based on their name
UPDATE "dive_sites" 
SET "dive_site_id" = LOWER(REPLACE(REPLACE(name, ' ', '_'), '-', '_'))
WHERE "dive_site_id" IS NULL;

-- Now make dive_site_id NOT NULL and add unique constraint
ALTER TABLE "dive_sites" ALTER COLUMN "dive_site_id" SET NOT NULL;
ALTER TABLE "dive_sites" ADD CONSTRAINT "dive_sites_dive_site_id_unique" UNIQUE("dive_site_id");

-- Set updated_at to NOT NULL with default
ALTER TABLE "dive_sites" ALTER COLUMN "updated_at" SET NOT NULL;
ALTER TABLE "dive_sites" ALTER COLUMN "updated_at" SET DEFAULT now();
