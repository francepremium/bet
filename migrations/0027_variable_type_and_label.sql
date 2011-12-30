ALTER TABLE "bookmaker_bettype"
        DROP COLUMN "variable";
ALTER TABLE "bookmaker_bettype"
        ADD "variable_type" varchar(20);
ALTER TABLE "bookmaker_bettype"
        ADD "variable_label_en" varchar(200);
ALTER TABLE "bookmaker_bettype"
        ADD "variable_label" varchar(200);
ALTER TABLE "bookmaker_bettype"
        ADD "variable_label_fr" varchar(200);

