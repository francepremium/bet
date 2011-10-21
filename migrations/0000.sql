### New Model: admin.LogEntry
CREATE TABLE "django_admin_log" (
    "id" serial NOT NULL PRIMARY KEY,
    "action_time" timestamp with time zone NOT NULL,
    "user_id" integer NOT NULL,
    "content_type_id" integer,
    "object_id" text,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint CHECK ("action_flag" >= 0) NOT NULL,
    "change_message" text NOT NULL
)
;
### New Model: auth.Permission
CREATE TABLE "auth_permission" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "content_type_id" integer NOT NULL,
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
)
;
### New Model: auth.Group_permissions
CREATE TABLE "auth_group_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "group_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id")
)
;
### New Model: auth.Group
CREATE TABLE "auth_group" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
)
;
ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "group_id_refs_id_3cea63fe" FOREIGN KEY ("group_id") REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: auth.User_user_permissions
CREATE TABLE "auth_user_user_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
)
;
### New Model: auth.User_groups
CREATE TABLE "auth_user_groups" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
)
;
### New Model: auth.User
CREATE TABLE "auth_user" (
    "id" serial NOT NULL PRIMARY KEY,
    "username" varchar(30) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "email" varchar(75) NOT NULL,
    "password" varchar(128) NOT NULL,
    "is_staff" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "is_superuser" boolean NOT NULL,
    "last_login" timestamp with time zone NOT NULL,
    "date_joined" timestamp with time zone NOT NULL
)
;
ALTER TABLE "django_admin_log" ADD CONSTRAINT "user_id_refs_id_c8665aa" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "auth_user_user_permissions" ADD CONSTRAINT "user_id_refs_id_dfbab7d" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "auth_user_groups" ADD CONSTRAINT "user_id_refs_id_7ceef80f" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: auth.Message
CREATE TABLE "auth_message" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "message" text NOT NULL
)
;
### New Model: contenttypes.ContentType
CREATE TABLE "django_content_type" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
)
;
ALTER TABLE "django_admin_log" ADD CONSTRAINT "content_type_id_refs_id_288599e6" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "auth_permission" ADD CONSTRAINT "content_type_id_refs_id_728de91f" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: sessions.Session
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" timestamp with time zone NOT NULL
)
;
### New Model: sites.Site
CREATE TABLE "django_site" (
    "id" serial NOT NULL PRIMARY KEY,
    "domain" varchar(100) NOT NULL,
    "name" varchar(50) NOT NULL
)
;
### New Model: comments.Comment
CREATE TABLE "django_comments" (
    "id" serial NOT NULL PRIMARY KEY,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_pk" text NOT NULL,
    "site_id" integer NOT NULL REFERENCES "django_site" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_name" varchar(50) NOT NULL,
    "user_email" varchar(75) NOT NULL,
    "user_url" varchar(200) NOT NULL,
    "comment" text NOT NULL,
    "submit_date" timestamp with time zone NOT NULL,
    "ip_address" inet,
    "is_public" boolean NOT NULL,
    "is_removed" boolean NOT NULL
)
;
### New Model: comments.CommentFlag
CREATE TABLE "django_comment_flags" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "comment_id" integer NOT NULL REFERENCES "django_comments" ("id") DEFERRABLE INITIALLY DEFERRED,
    "flag" varchar(30) NOT NULL,
    "flag_date" timestamp with time zone NOT NULL,
    UNIQUE ("user_id", "comment_id", "flag")
)
;
### New Model: emailconfirmation.EmailAddress
CREATE TABLE "emailconfirmation_emailaddress" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "email" varchar(75) NOT NULL,
    "verified" boolean NOT NULL,
    "primary" boolean NOT NULL,
    UNIQUE ("user_id", "email")
)
;
### New Model: emailconfirmation.EmailConfirmation
CREATE TABLE "emailconfirmation_emailconfirmation" (
    "id" serial NOT NULL PRIMARY KEY,
    "email_address_id" integer NOT NULL REFERENCES "emailconfirmation_emailaddress" ("id") DEFERRABLE INITIALLY DEFERRED,
    "sent" timestamp with time zone NOT NULL,
    "confirmation_key" varchar(40) NOT NULL
)
;
### New Model: account.Account
CREATE TABLE "account_account" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "timezone" varchar(100) NOT NULL,
    "language" varchar(10) NOT NULL
)
;
### New Model: account.OtherServiceInfo
CREATE TABLE "account_otherserviceinfo" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "key" varchar(50) NOT NULL,
    "value" text NOT NULL,
    UNIQUE ("user_id", "key")
)
;
### New Model: account.PasswordReset
CREATE TABLE "account_passwordreset" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "temp_key" varchar(100) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    "reset" boolean NOT NULL
)
;
### New Model: mailer.Message
CREATE TABLE "mailer_message" (
    "id" serial NOT NULL PRIMARY KEY,
    "message_data" text NOT NULL,
    "when_added" timestamp with time zone NOT NULL,
    "priority" varchar(1) NOT NULL
)
;
### New Model: mailer.DontSendEntry
CREATE TABLE "mailer_dontsendentry" (
    "id" serial NOT NULL PRIMARY KEY,
    "to_address" varchar(75) NOT NULL,
    "when_added" timestamp with time zone NOT NULL
)
;
### New Model: mailer.MessageLog
CREATE TABLE "mailer_messagelog" (
    "id" serial NOT NULL PRIMARY KEY,
    "message_data" text NOT NULL,
    "when_added" timestamp with time zone NOT NULL,
    "priority" varchar(1) NOT NULL,
    "when_attempted" timestamp with time zone NOT NULL,
    "result" varchar(1) NOT NULL,
    "log_message" text NOT NULL
)
;
### New Model: avatar.Avatar
CREATE TABLE "avatar_avatar" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "primary" boolean NOT NULL,
    "avatar" varchar(1024) NOT NULL,
    "date_uploaded" timestamp with time zone NOT NULL
)
;
### New Model: actstream.Follow
CREATE TABLE "actstream_follow" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0) NOT NULL,
    UNIQUE ("user_id", "content_type_id", "object_id")
)
;
### New Model: actstream.Action
CREATE TABLE "actstream_action" (
    "id" serial NOT NULL PRIMARY KEY,
    "actor_content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "actor_object_id" integer CHECK ("actor_object_id" >= 0) NOT NULL,
    "verb" varchar(255) NOT NULL,
    "description" text,
    "target_content_type_id" integer REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "target_object_id" integer CHECK ("target_object_id" >= 0),
    "action_object_content_type_id" integer REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "action_object_object_id" integer CHECK ("action_object_object_id" >= 0),
    "timestamp" timestamp with time zone NOT NULL,
    "public" boolean NOT NULL
)
;
### New Model: django_messages.Message
CREATE TABLE "django_messages_message" (
    "id" serial NOT NULL PRIMARY KEY,
    "subject" varchar(120) NOT NULL,
    "body" text NOT NULL,
    "sender_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "recipient_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "parent_msg_id" integer,
    "sent_at" timestamp with time zone,
    "read_at" timestamp with time zone,
    "replied_at" timestamp with time zone,
    "sender_deleted_at" timestamp with time zone,
    "recipient_deleted_at" timestamp with time zone
)
;
ALTER TABLE "django_messages_message" ADD CONSTRAINT "parent_msg_id_refs_id_5d7fc805" FOREIGN KEY ("parent_msg_id") REFERENCES "django_messages_message" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Area
CREATE TABLE "gsm_area" (
    "id" serial NOT NULL PRIMARY KEY,
    "parent_id" integer,
    "country_code" varchar(3) NOT NULL,
    "country_code_2" varchar(2) NOT NULL,
    "gsm_id" integer NOT NULL UNIQUE,
    "name" varchar(50) NOT NULL,
    "name_en" varchar(50),
    "name_fr" varchar(50),
    "_order" integer NOT NULL
)
;
ALTER TABLE "gsm_area" ADD CONSTRAINT "parent_id_refs_id_2a8895b3" FOREIGN KEY ("parent_id") REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Sport_fans
CREATE TABLE "gsm_sport_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("sport_id", "user_id")
)
;
### New Model: gsm.Sport
CREATE TABLE "gsm_sport" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(30) NOT NULL,
    "slug" varchar(20) NOT NULL
)
;
ALTER TABLE "gsm_sport_fans" ADD CONSTRAINT "sport_id_refs_id_14d14f2f" FOREIGN KEY ("sport_id") REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.GsmEntity_fans
CREATE TABLE "gsm_gsmentity_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "gsmentity_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("gsmentity_id", "user_id")
)
;
### New Model: gsm.GsmEntity
CREATE TABLE "gsm_gsmentity" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gsm_id" integer NOT NULL,
    "tag" varchar(32) NOT NULL,
    "area_id" integer REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(150),
    "name_en" varchar(150),
    "name_fr" varchar(150),
    "last_updated" timestamp with time zone,
    UNIQUE ("sport_id", "tag", "gsm_id")
)
;
ALTER TABLE "gsm_gsmentity_fans" ADD CONSTRAINT "gsmentity_id_refs_id_16348891" FOREIGN KEY ("gsmentity_id") REFERENCES "gsm_gsmentity" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Championship_fans
CREATE TABLE "gsm_championship_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "championship_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("championship_id", "user_id")
)
;
### New Model: gsm.Championship
CREATE TABLE "gsm_championship" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gsm_id" integer NOT NULL,
    "tag" varchar(32) NOT NULL,
    "area_id" integer REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(150),
    "name_en" varchar(150),
    "name_fr" varchar(150),
    "last_updated" timestamp with time zone,
    UNIQUE ("sport_id", "tag", "gsm_id")
)
;
ALTER TABLE "gsm_championship_fans" ADD CONSTRAINT "championship_id_refs_id_6bb30737" FOREIGN KEY ("championship_id") REFERENCES "gsm_championship" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Competition_fans
CREATE TABLE "gsm_competition_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "competition_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("competition_id", "user_id")
)
;
### New Model: gsm.Competition
CREATE TABLE "gsm_competition" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gsm_id" integer NOT NULL,
    "tag" varchar(32) NOT NULL,
    "area_id" integer REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(150),
    "name_en" varchar(150),
    "name_fr" varchar(150),
    "last_updated" timestamp with time zone,
    "championship_id" integer REFERENCES "gsm_championship" ("id") DEFERRABLE INITIALLY DEFERRED,
    "competition_type" varchar(32),
    "competition_format" varchar(32),
    "court_type" varchar(12),
    "team_type" varchar(12),
    "display_order" integer,
    "is_nationnal" boolean NOT NULL,
    UNIQUE ("sport_id", "tag", "gsm_id")
)
;
ALTER TABLE "gsm_competition_fans" ADD CONSTRAINT "competition_id_refs_id_3b4b651b" FOREIGN KEY ("competition_id") REFERENCES "gsm_competition" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Season_fans
CREATE TABLE "gsm_season_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "season_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("season_id", "user_id")
)
;
### New Model: gsm.Season
CREATE TABLE "gsm_season" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gsm_id" integer NOT NULL,
    "tag" varchar(32) NOT NULL,
    "area_id" integer REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(150),
    "name_en" varchar(150),
    "name_fr" varchar(150),
    "last_updated" timestamp with time zone,
    "competition_id" integer NOT NULL REFERENCES "gsm_competition" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gender" varchar(12),
    "prize_money" integer,
    "prize_currency" varchar(3),
    "season_type" varchar(12),
    "start_date" timestamp with time zone,
    "end_date" timestamp with time zone,
    UNIQUE ("sport_id", "tag", "gsm_id")
)
;
ALTER TABLE "gsm_season_fans" ADD CONSTRAINT "season_id_refs_id_4b1580af" FOREIGN KEY ("season_id") REFERENCES "gsm_season" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Round_fans
CREATE TABLE "gsm_round_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "round_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("round_id", "user_id")
)
;
### New Model: gsm.Round
CREATE TABLE "gsm_round" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gsm_id" integer NOT NULL,
    "tag" varchar(32) NOT NULL,
    "area_id" integer REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(150),
    "name_en" varchar(150),
    "name_fr" varchar(150),
    "last_updated" timestamp with time zone,
    "season_id" integer NOT NULL REFERENCES "gsm_season" ("id") DEFERRABLE INITIALLY DEFERRED,
    "start_date" timestamp with time zone,
    "end_date" timestamp with time zone,
    "round_type" varchar(12),
    "scoring_system" varchar(12),
    "groups" integer NOT NULL,
    "has_outgroup_matches" boolean NOT NULL,
    UNIQUE ("sport_id", "tag", "gsm_id")
)
;
ALTER TABLE "gsm_round_fans" ADD CONSTRAINT "round_id_refs_id_74c6f50d" FOREIGN KEY ("round_id") REFERENCES "gsm_round" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: gsm.Session_fans
CREATE TABLE "gsm_session_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "session_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("session_id", "user_id")
)
;
### New Model: gsm.Session
CREATE TABLE "gsm_session" (
    "id" serial NOT NULL PRIMARY KEY,
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "gsm_id" integer NOT NULL,
    "tag" varchar(32) NOT NULL,
    "area_id" integer REFERENCES "gsm_area" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(150),
    "name_en" varchar(150),
    "name_fr" varchar(150),
    "last_updated" timestamp with time zone,
    "season_id" integer REFERENCES "gsm_season" ("id") DEFERRABLE INITIALLY DEFERRED,
    "session_round_id" integer REFERENCES "gsm_round" ("id") DEFERRABLE INITIALLY DEFERRED,
    "draw" boolean,
    "A1_score" integer,
    "A2_score" integer,
    "A3_score" integer,
    "A4_score" integer,
    "A5_score" integer,
    "B1_score" integer,
    "B2_score" integer,
    "B3_score" integer,
    "B4_score" integer,
    "B5_score" integer,
    "A_score" integer,
    "B_score" integer,
    "A_ets" integer,
    "B_ets" integer,
    "penalty" varchar(1),
    "actual_start_datetime" timestamp with time zone,
    "start_datetime" timestamp with time zone,
    "time_unknown" boolean NOT NULL,
    "status" varchar(12) NOT NULL,
    "gameweek" integer,
    "winner_id" integer REFERENCES "gsm_gsmentity" ("id") DEFERRABLE INITIALLY DEFERRED,
    "oponnent_A_id" integer REFERENCES "gsm_gsmentity" ("id") DEFERRABLE INITIALLY DEFERRED,
    "oponnent_B_id" integer REFERENCES "gsm_gsmentity" ("id") DEFERRABLE INITIALLY DEFERRED,
    "oponnent_A_name" varchar(60),
    "oponnent_B_name" varchar(60)
)
;
ALTER TABLE "gsm_session_fans" ADD CONSTRAINT "session_id_refs_id_f880831" FOREIGN KEY ("session_id") REFERENCES "gsm_session" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: bookmaker.Bookmaker_bettype
CREATE TABLE "bookmaker_bookmaker_bettype" (
    "id" serial NOT NULL PRIMARY KEY,
    "bookmaker_id" integer NOT NULL,
    "bettype_id" integer NOT NULL,
    UNIQUE ("bookmaker_id", "bettype_id")
)
;
### New Model: bookmaker.Bookmaker_fans
CREATE TABLE "bookmaker_bookmaker_fans" (
    "id" serial NOT NULL PRIMARY KEY,
    "bookmaker_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("bookmaker_id", "user_id")
)
;
### New Model: bookmaker.Bookmaker
CREATE TABLE "bookmaker_bookmaker" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(100) NOT NULL UNIQUE,
    "creation_date" varchar(15),
    "address" text,
    "url" varchar(200) NOT NULL,
    "email" varchar(75) NOT NULL,
    "live_bets" boolean NOT NULL,
    "logo" varchar(100)
)
;
ALTER TABLE "bookmaker_bookmaker_bettype" ADD CONSTRAINT "bookmaker_id_refs_id_781f397f" FOREIGN KEY ("bookmaker_id") REFERENCES "bookmaker_bookmaker" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "bookmaker_bookmaker_fans" ADD CONSTRAINT "bookmaker_id_refs_id_175a0a6f" FOREIGN KEY ("bookmaker_id") REFERENCES "bookmaker_bookmaker" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: bookmaker.BetType
CREATE TABLE "bookmaker_bettype" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "name_en" varchar(100),
    "name_fr" varchar(100),
    "sport_id" integer NOT NULL REFERENCES "gsm_sport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "creation_bookmaker_id" integer REFERENCES "bookmaker_bookmaker" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("name_fr", "sport_id"),
    UNIQUE ("name_en", "sport_id")
)
;
ALTER TABLE "bookmaker_bookmaker_bettype" ADD CONSTRAINT "bettype_id_refs_id_5d4bf601" FOREIGN KEY ("bettype_id") REFERENCES "bookmaker_bettype" ("id") DEFERRABLE INITIALLY DEFERRED;
### New Model: bookmaker.BetChoice
CREATE TABLE "bookmaker_betchoice" (
    "id" serial NOT NULL PRIMARY KEY,
    "bettype_id" integer NOT NULL REFERENCES "bookmaker_bettype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(100) NOT NULL,
    "name_en" varchar(100),
    "name_fr" varchar(100)
)
;
### New Model: bet.BetProfile
CREATE TABLE "bet_betprofile" (
    "user_id" integer NOT NULL PRIMARY KEY REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "offside_on" timestamp with time zone
)
;
### New Model: bet.Ticket
CREATE TABLE "bet_ticket" (
    "id" serial NOT NULL PRIMARY KEY,
    "bookmaker_id" integer NOT NULL REFERENCES "bookmaker_bookmaker" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "stake" integer NOT NULL,
    "status" integer NOT NULL
)
;
### New Model: bet.Bet
CREATE TABLE "bet_bet" (
    "id" serial NOT NULL PRIMARY KEY,
    "bettype_id" integer NOT NULL REFERENCES "bookmaker_bettype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "choice_id" integer REFERENCES "bookmaker_betchoice" ("id") DEFERRABLE INITIALLY DEFERRED,
    "session_id" integer NOT NULL REFERENCES "gsm_session" ("id") DEFERRABLE INITIALLY DEFERRED,
    "ticket_id" integer NOT NULL REFERENCES "bet_ticket" ("id") DEFERRABLE INITIALLY DEFERRED,
    "odds" numeric(4, 2) NOT NULL,
    "text" text,
    "upload" varchar(100),
    "status" integer NOT NULL,
    "correction" integer NOT NULL
)
;
### New Model: bet.Event
CREATE TABLE "bet_event" (
    "id" serial NOT NULL PRIMARY KEY,
    "bet_id" integer NOT NULL REFERENCES "bet_bet" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "correction" integer NOT NULL,
    "datetime" timestamp with time zone NOT NULL,
    "kind" integer NOT NULL,
    "valid" boolean NOT NULL
)
;
### New Model: clan.Clan
CREATE TABLE "clan_clan" (
    "id" serial NOT NULL PRIMARY KEY,
    "creation_user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "creation_datetime" timestamp with time zone NOT NULL,
    "modification_datetime" timestamp with time zone NOT NULL,
    "name" varchar(100) NOT NULL,
    "slug" varchar(50) NOT NULL UNIQUE,
    "auto_approve" boolean NOT NULL,
    "description" text,
    "image" varchar(100) NOT NULL,
    "kind" integer NOT NULL
)
;
### New Model: clan.Membership
CREATE TABLE "clan_membership" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "clan_id" integer NOT NULL REFERENCES "clan_clan" ("id") DEFERRABLE INITIALLY DEFERRED,
    "creation_datetime" timestamp with time zone NOT NULL,
    "modification_datetime" timestamp with time zone NOT NULL,
    "modification_user_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "kind" integer,
    UNIQUE ("user_id", "clan_id")
)
;
### New Model: article.Article
CREATE TABLE "article_article" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "slug" varchar(50) NOT NULL UNIQUE,
    "creation_user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "creation_datetime" timestamp with time zone NOT NULL,
    "modification_datetime" timestamp with time zone NOT NULL,
    "text" text NOT NULL
)
;
### New Model: django_openid.Nonce
CREATE TABLE "django_openid_nonce" (
    "id" serial NOT NULL PRIMARY KEY,
    "server_url" varchar(255) NOT NULL,
    "timestamp" integer NOT NULL,
    "salt" varchar(40) NOT NULL
)
;
### New Model: django_openid.Association
CREATE TABLE "django_openid_association" (
    "id" serial NOT NULL PRIMARY KEY,
    "server_url" text NOT NULL,
    "handle" varchar(255) NOT NULL,
    "secret" text NOT NULL,
    "issued" integer NOT NULL,
    "lifetime" integer NOT NULL,
    "assoc_type" text NOT NULL
)
;
### New Model: django_openid.UserOpenidAssociation
CREATE TABLE "django_openid_useropenidassociation" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "openid" varchar(255) NOT NULL,
    "created" timestamp with time zone NOT NULL
)
;
CREATE INDEX "django_admin_log_user_id" ON "django_admin_log" ("user_id");
CREATE INDEX "django_admin_log_content_type_id" ON "django_admin_log" ("content_type_id");
CREATE INDEX "auth_permission_content_type_id" ON "auth_permission" ("content_type_id");
CREATE INDEX "auth_group_permissions_group_id" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_user_user_permissions_user_id" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "auth_user_groups_user_id" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id" ON "auth_user_groups" ("group_id");
CREATE INDEX "auth_message_user_id" ON "auth_message" ("user_id");
CREATE INDEX "django_session_expire_date" ON "django_session" ("expire_date");
CREATE INDEX "django_comments_content_type_id" ON "django_comments" ("content_type_id");
CREATE INDEX "django_comments_site_id" ON "django_comments" ("site_id");
CREATE INDEX "django_comments_user_id" ON "django_comments" ("user_id");
CREATE INDEX "django_comment_flags_user_id" ON "django_comment_flags" ("user_id");
CREATE INDEX "django_comment_flags_comment_id" ON "django_comment_flags" ("comment_id");
CREATE INDEX "django_comment_flags_flag" ON "django_comment_flags" ("flag");
CREATE INDEX "django_comment_flags_flag_like" ON "django_comment_flags" ("flag" varchar_pattern_ops);
CREATE INDEX "emailconfirmation_emailaddress_user_id" ON "emailconfirmation_emailaddress" ("user_id");
CREATE INDEX "emailconfirmation_emailconfirmation_email_address_id" ON "emailconfirmation_emailconfirmation" ("email_address_id");
CREATE INDEX "account_otherserviceinfo_user_id" ON "account_otherserviceinfo" ("user_id");
CREATE INDEX "account_passwordreset_user_id" ON "account_passwordreset" ("user_id");
CREATE INDEX "avatar_avatar_user_id" ON "avatar_avatar" ("user_id");
CREATE INDEX "actstream_follow_user_id" ON "actstream_follow" ("user_id");
CREATE INDEX "actstream_follow_content_type_id" ON "actstream_follow" ("content_type_id");
CREATE INDEX "actstream_action_actor_content_type_id" ON "actstream_action" ("actor_content_type_id");
CREATE INDEX "actstream_action_target_content_type_id" ON "actstream_action" ("target_content_type_id");
CREATE INDEX "actstream_action_action_object_content_type_id" ON "actstream_action" ("action_object_content_type_id");
CREATE INDEX "django_messages_message_sender_id" ON "django_messages_message" ("sender_id");
CREATE INDEX "django_messages_message_recipient_id" ON "django_messages_message" ("recipient_id");
CREATE INDEX "django_messages_message_parent_msg_id" ON "django_messages_message" ("parent_msg_id");
CREATE INDEX "gsm_area_parent_id" ON "gsm_area" ("parent_id");
CREATE INDEX "gsm_sport_fans_sport_id" ON "gsm_sport_fans" ("sport_id");
CREATE INDEX "gsm_sport_fans_user_id" ON "gsm_sport_fans" ("user_id");
CREATE INDEX "gsm_gsmentity_fans_gsmentity_id" ON "gsm_gsmentity_fans" ("gsmentity_id");
CREATE INDEX "gsm_gsmentity_fans_user_id" ON "gsm_gsmentity_fans" ("user_id");
CREATE INDEX "gsm_gsmentity_sport_id" ON "gsm_gsmentity" ("sport_id");
CREATE INDEX "gsm_gsmentity_area_id" ON "gsm_gsmentity" ("area_id");
CREATE INDEX "gsm_championship_fans_championship_id" ON "gsm_championship_fans" ("championship_id");
CREATE INDEX "gsm_championship_fans_user_id" ON "gsm_championship_fans" ("user_id");
CREATE INDEX "gsm_championship_sport_id" ON "gsm_championship" ("sport_id");
CREATE INDEX "gsm_championship_area_id" ON "gsm_championship" ("area_id");
CREATE INDEX "gsm_competition_fans_competition_id" ON "gsm_competition_fans" ("competition_id");
CREATE INDEX "gsm_competition_fans_user_id" ON "gsm_competition_fans" ("user_id");
CREATE INDEX "gsm_competition_sport_id" ON "gsm_competition" ("sport_id");
CREATE INDEX "gsm_competition_area_id" ON "gsm_competition" ("area_id");
CREATE INDEX "gsm_competition_championship_id" ON "gsm_competition" ("championship_id");
CREATE INDEX "gsm_season_fans_season_id" ON "gsm_season_fans" ("season_id");
CREATE INDEX "gsm_season_fans_user_id" ON "gsm_season_fans" ("user_id");
CREATE INDEX "gsm_season_sport_id" ON "gsm_season" ("sport_id");
CREATE INDEX "gsm_season_area_id" ON "gsm_season" ("area_id");
CREATE INDEX "gsm_season_competition_id" ON "gsm_season" ("competition_id");
CREATE INDEX "gsm_round_fans_round_id" ON "gsm_round_fans" ("round_id");
CREATE INDEX "gsm_round_fans_user_id" ON "gsm_round_fans" ("user_id");
CREATE INDEX "gsm_round_sport_id" ON "gsm_round" ("sport_id");
CREATE INDEX "gsm_round_area_id" ON "gsm_round" ("area_id");
CREATE INDEX "gsm_round_season_id" ON "gsm_round" ("season_id");
CREATE INDEX "gsm_session_fans_session_id" ON "gsm_session_fans" ("session_id");
CREATE INDEX "gsm_session_fans_user_id" ON "gsm_session_fans" ("user_id");
CREATE INDEX "gsm_session_sport_id" ON "gsm_session" ("sport_id");
CREATE INDEX "gsm_session_area_id" ON "gsm_session" ("area_id");
CREATE INDEX "gsm_session_season_id" ON "gsm_session" ("season_id");
CREATE INDEX "gsm_session_session_round_id" ON "gsm_session" ("session_round_id");
CREATE INDEX "gsm_session_winner_id" ON "gsm_session" ("winner_id");
CREATE INDEX "gsm_session_oponnent_A_id" ON "gsm_session" ("oponnent_A_id");
CREATE INDEX "gsm_session_oponnent_B_id" ON "gsm_session" ("oponnent_B_id");
CREATE INDEX "bookmaker_bookmaker_bettype_bookmaker_id" ON "bookmaker_bookmaker_bettype" ("bookmaker_id");
CREATE INDEX "bookmaker_bookmaker_bettype_bettype_id" ON "bookmaker_bookmaker_bettype" ("bettype_id");
CREATE INDEX "bookmaker_bookmaker_fans_bookmaker_id" ON "bookmaker_bookmaker_fans" ("bookmaker_id");
CREATE INDEX "bookmaker_bookmaker_fans_user_id" ON "bookmaker_bookmaker_fans" ("user_id");
CREATE INDEX "bookmaker_bettype_sport_id" ON "bookmaker_bettype" ("sport_id");
CREATE INDEX "bookmaker_bettype_creation_bookmaker_id" ON "bookmaker_bettype" ("creation_bookmaker_id");
CREATE INDEX "bookmaker_betchoice_bettype_id" ON "bookmaker_betchoice" ("bettype_id");
CREATE INDEX "bet_ticket_bookmaker_id" ON "bet_ticket" ("bookmaker_id");
CREATE INDEX "bet_ticket_user_id" ON "bet_ticket" ("user_id");
CREATE INDEX "bet_bet_bettype_id" ON "bet_bet" ("bettype_id");
CREATE INDEX "bet_bet_choice_id" ON "bet_bet" ("choice_id");
CREATE INDEX "bet_bet_session_id" ON "bet_bet" ("session_id");
CREATE INDEX "bet_bet_ticket_id" ON "bet_bet" ("ticket_id");
CREATE INDEX "bet_event_bet_id" ON "bet_event" ("bet_id");
CREATE INDEX "bet_event_user_id" ON "bet_event" ("user_id");
CREATE INDEX "clan_clan_creation_user_id" ON "clan_clan" ("creation_user_id");
CREATE INDEX "clan_membership_user_id" ON "clan_membership" ("user_id");
CREATE INDEX "clan_membership_clan_id" ON "clan_membership" ("clan_id");
CREATE INDEX "clan_membership_modification_user_id" ON "clan_membership" ("modification_user_id");
CREATE INDEX "article_article_creation_user_id" ON "article_article" ("creation_user_id");
CREATE INDEX "django_openid_useropenidassociation_user_id" ON "django_openid_useropenidassociation" ("user_id");
