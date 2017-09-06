CREATE TABLE facebook.posts_{} (
    post_id            VARCHAR(50) NOT NULL PRIMARY KEY,
    poster_id          VARCHAR(50),
    poster_name        VARCHAR(50),
    message            TEXT,
    link               TEXT,
    tags               TEXT,
    attachment         TEXT, 
    time_created       DATETIME,
    description        TEXT,
    reactions_like     INT,
    reactions_love     INT,
    reactions_wow      INT,
    reactions_haha     INT,
    reactions_sad      INT,
    reactions_angry    INT,
    reactions_thankful INT
)
