CREATE TABLE "subscription" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL
)
;
CREATE INDEX "subscription_user_id" ON "subscription" ("user_id");
CREATE INDEX "subscription_content_type_id" ON "subscription" ("content_type_id");

