CREATE TABLE "tools_attribute" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "value" varchar(1024) NOT NULL,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0) NOT NULL
)
;
### New Model: cms.Template
CREATE TABLE "cms_template" (
    "id" serial NOT NULL PRIMARY KEY,
    "path" varchar(500) NOT NULL,
    "description" varchar(200) NOT NULL,
    "content" text NOT NULL
)
;
### New Model: cms.Page
CREATE TABLE "cms_page" (
    "id" serial NOT NULL PRIMARY KEY,
    "parent_id" integer,
    "path" varchar(50) NOT NULL,
    "title" varchar(512) NOT NULL,
    "is_published" boolean NOT NULL,
    "template_id" integer REFERENCES "cms_template" ("id") DEFERRABLE INITIALLY DEFERRED,
    "content" text NOT NULL,
    UNIQUE ("parent_id", "path")
)
;
ALTER TABLE "cms_page" ADD CONSTRAINT "parent_id_refs_id_653a773" FOREIGN KEY ("parent_id") REFERENCES "cms_page" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: cms.Fragment
CREATE TABLE "cms_fragment" (
    "id" serial NOT NULL PRIMARY KEY,
    "page_id" integer NOT NULL REFERENCES "cms_page" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(200) NOT NULL,
    "content" text NOT NULL,
    UNIQUE ("page_id", "name")
)
;
### New Model: cms.PageAccess
CREATE TABLE "cms_pageaccess" (
    "id" serial NOT NULL PRIMARY KEY,
    "page_id" integer NOT NULL REFERENCES "cms_page" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" integer REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permit" boolean NOT NULL,
    UNIQUE ("page_id", "group_id")
)
;
### New Model: cms.StyleSheet
CREATE TABLE "cms_stylesheet" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "description" varchar(1024) NOT NULL,
    "content" text NOT NULL
)
;
### New Model: cms.ContextVariable
CREATE TABLE "cms_contextvariable" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(64) NOT NULL,
    "group" varchar(64) NOT NULL,
    "description" varchar(200) NOT NULL,
    "type" varchar(32) NOT NULL,
    "value" varchar(1024) NOT NULL
)
;
CREATE INDEX "tools_attribute_name" ON "tools_attribute" ("name");
CREATE INDEX "tools_attribute_name_like" ON "tools_attribute" ("name" varchar_pattern_ops);
CREATE INDEX "tools_attribute_content_type_id" ON "tools_attribute" ("content_type_id");
CREATE INDEX "cms_template_path" ON "cms_template" ("path");
CREATE INDEX "cms_template_path_like" ON "cms_template" ("path" varchar_pattern_ops);
CREATE INDEX "cms_page_parent_id" ON "cms_page" ("parent_id");
CREATE INDEX "cms_page_path" ON "cms_page" ("path");
CREATE INDEX "cms_page_path_like" ON "cms_page" ("path" varchar_pattern_ops);
CREATE INDEX "cms_page_template_id" ON "cms_page" ("template_id");
CREATE INDEX "cms_fragment_page_id" ON "cms_fragment" ("page_id");
CREATE INDEX "cms_pageaccess_page_id" ON "cms_pageaccess" ("page_id");
CREATE INDEX "cms_pageaccess_group_id" ON "cms_pageaccess" ("group_id");
CREATE INDEX "cms_stylesheet_name" ON "cms_stylesheet" ("name");
CREATE INDEX "cms_stylesheet_name_like" ON "cms_stylesheet" ("name" varchar_pattern_ops);

