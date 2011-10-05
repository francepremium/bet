CREATE TABLE "taggit_tag" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "slug" varchar(100) NOT NULL UNIQUE
)
;
CREATE TABLE "taggit_taggeditem" (
    "id" serial NOT NULL PRIMARY KEY,
    "tag_id" integer NOT NULL REFERENCES "taggit_tag" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer NOT NULL,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE INDEX "taggit_taggeditem_tag_id" ON "taggit_taggeditem" ("tag_id");
CREATE INDEX "taggit_taggeditem_object_id" ON "taggit_taggeditem" ("object_id");
CREATE INDEX "taggit_taggeditem_content_type_id" ON "taggit_taggeditem" ("content_type_id");

