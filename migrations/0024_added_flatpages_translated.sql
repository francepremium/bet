### New Model: flatpages.FlatPage_sites
CREATE TABLE "django_flatpage_sites" (
    "id" serial NOT NULL PRIMARY KEY,
    "flatpage_id" integer NOT NULL,
    "site_id" integer NOT NULL REFERENCES "django_site" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("flatpage_id", "site_id")
)
;
### New Model: flatpages.FlatPage
CREATE TABLE "django_flatpage" (
    "id" serial NOT NULL PRIMARY KEY,
    "url" varchar(100) NOT NULL,
    "title" varchar(200) NOT NULL,
    "title_en" varchar(200),
    "title_fr" varchar(200),
    "content" text NOT NULL,
    "content_en" text,
    "content_fr" text,
    "enable_comments" boolean NOT NULL,
    "template_name" varchar(70) NOT NULL,
    "registration_required" boolean NOT NULL
)
;
ALTER TABLE "django_flatpage_sites" ADD CONSTRAINT "flatpage_id_refs_id_c0e84f5a" FOREIGN KEY ("flatpage_id") REFERENCES "django_flatpage" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "django_flatpage_sites_flatpage_id" ON "django_flatpage_sites" ("flatpage_id");
CREATE INDEX "django_flatpage_sites_site_id" ON "django_flatpage_sites" ("site_id");
CREATE INDEX "django_flatpage_url" ON "django_flatpage" ("url");
CREATE INDEX "django_flatpage_url_like" ON "django_flatpage" ("url" varchar_pattern_ops);
