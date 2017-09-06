CREATE TABLE indeed.{}(
    review_id                VARCHAR(30) NOT NULL PRIMARY KEY,
    overall_review_score     INT,
    job_work_life_balance    INT,
    compensation_benefits    INT,
    job_security_advancement INT,
    management               INT,
    job_culture              INT,
    poster_role              VARCHAR(90),
    review_title             VARCHAR(90),
    poster_status            VARCHAR(60),
    poster_location          VARCHAR(60),
    post_date                DATETIME,
    review_text              TEXT,
    pros                     TEXT,
    cons                     TEXT
);