-- Aumne AI sample data
-- Uses INSERT OR IGNORE to avoid duplicate IDs.

INSERT OR IGNORE INTO posts
    (id, title, content, status, flagged_reasons, created_at)
VALUES
(
    1001,
    'Introduction to Artificial Intelligence',
    'Artificial intelligence enables computer systems to perform tasks that typically require human intelligence. Responsible development and thoughtful evaluation help make these systems useful and reliable.',
    'draft',
    NULL,
    CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO posts
    (id, title, content, status, flagged_reasons, created_at)
VALUES
(
    1002,
    'Learning Python Programming',
    'Python is a versatile programming language used in web development, data analysis, automation, and machine learning. Beginners can develop strong programming skills by practising regularly and building small projects.',
    'draft',
    NULL,
    CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO posts
    (id, title, content, status, flagged_reasons, created_at)
VALUES
(
    1003,
    'Benefits of Regular Learning',
    'Continuous learning helps people develop new skills, improve problem-solving abilities, and adapt to changing technologies. Setting realistic goals and reviewing progress regularly can make learning more effective.',
    'draft',
    NULL,
    CURRENT_TIMESTAMP
);