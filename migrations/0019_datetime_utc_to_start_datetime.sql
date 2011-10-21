ALTER TABLE "gsm_session"
        DROP COLUMN "datetime_utc";
ALTER TABLE "gsm_session"
        ADD "start_datetime" timestamp with time zone;

