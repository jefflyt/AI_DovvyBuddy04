ALTER TABLE "dive_sites" ADD COLUMN "dive_site_id" text NOT NULL;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD COLUMN "difficulty_rating" integer;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD COLUMN "depth_min_m" real;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD COLUMN "depth_max_m" real;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD COLUMN "tags" json;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD COLUMN "last_updated" timestamp with time zone;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD COLUMN "updated_at" timestamp with time zone DEFAULT now() NOT NULL;--> statement-breakpoint
ALTER TABLE "dive_sites" ADD CONSTRAINT "dive_sites_dive_site_id_unique" UNIQUE("dive_site_id");