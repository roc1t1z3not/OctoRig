-- SubVerse DB Backup 2024-12-01
-- WARNING: MD5 password hashes — crack with hashcat + rockyou.txt
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY, username TEXT, email TEXT,
  password_hash TEXT, role TEXT, karma INTEGER
);
INSERT INTO users VALUES
  (1,"admin","admin@subverse.local","36b809e24478355e344545720ea7e090","admin",9999),
  (2,"mod_alice","alice@subverse.local","7c6a180b36896a0a8c02787eeafb0e4c","moderator",4500),
  (3,"mod_bob","bob@subverse.local","0d107d09f5bbe40cade3de5c71e9e9b7","moderator",3200),
  (4,"sv_dan","dan.foster@mail.example","d5c0607301ad5d5c1528962a83992ac8","user",850),
  (5,"pixel_kate","kate.p@mail.example","e65c8afc9951f94fed8873a4c1e31a63","user",420),
  (6,"tech_marcus","marcus.t@mail.example","f25a2fc72690b780b2a14e140ef6a9e0","user",720),
  (7,"sara_q","sara.q@mail.example","cc25c0f861a83f5efadc6e1ba9d1269e","user",310),
  (8,"ghost_user","ghost@mail.example","b696aef7776367787253dc2acdd10279","user",55);
