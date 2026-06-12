-- SubVerse DB Backup 2025-05-01
-- WARNING: MD5 password hashes — crack with hashcat + rockyou.txt
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY, username TEXT, email TEXT,
  password_hash TEXT, role TEXT, karma INTEGER
);
INSERT INTO users VALUES
  (1,"admin","admin@subverse.local","36b809e24478355e344545720ea7e090","admin",9999),
  (2,"mod_alice","alice@subverse.local","7c6a180b36896a0a8c02787eeafb0e4c","moderator",4812),
  (3,"mod_bob","bob@subverse.local","0d107d09f5bbe40cade3de5c71e9e9b7","moderator",3541),
  (4,"cipher_dev","cipher@mail.example","d5c0607301ad5d5c1528962a83992ac8","user",967),
  (5,"rootkit_rose","rose.r@mail.example","e65c8afc9951f94fed8873a4c1e31a63","user",731),
  (6,"nullptr_","null@mail.example","f25a2fc72690b780b2a14e140ef6a9e0","user",889),
  (7,"hexdump_hero","hex@mail.example","cc25c0f861a83f5efadc6e1ba9d1269e","user",512),
  (8,"ghost_signal","ghost@mail.example","b696aef7776367787253dc2acdd10279","user",88),
  (9,"terminal_kai","kai.t@mail.example","1b3231655cebb7a1f783eddf27d254ca","user",344),
  (10,"sudo_sarah","sarah.sudo@mail.example","865d6c4a566268abf14e5da76c71bff9","user",278),
  (11,"packet_pete","pete.p@mail.example","5f4dcc3b5aa765d61d8327deb882cf99","user",193),
  (12,"devsec_dia","dia.d@mail.example","e10adc3949ba59abbe56e057f20f883e","user",441),
  (13,"shellcode_sam","sam.sc@mail.example","9a0364b9e99bb480dd25e1f0284c8555","user",302),
  (14,"xor_xena","xena.x@mail.example","8afa847f50a716e64932d995c8e7435a","user",215),
  (15,"fuzzr_felix","felix.fz@mail.example","8621ffdbc5698829397d97767ac13db3","user",167),
  (16,"netcat_neo","neo.nc@mail.example","e99a18c428cb38d5f260853678922e03","user",389),
  (17,"bytesmith","byte.s@mail.example","d0763edaa9d9bd2a9516280e9044d885","user",122),
  (18,"vuln_viv","viv.v@mail.example","67aeea294e1cb515236c73ac6e6eaa93","user",267),
  (19,"traceroute_ty","ty.tr@mail.example","d8578edf8458ce06fbc5bb76a58c5ca4","user",99),
  (20,"asm_archer","archer.asm@mail.example","84d961568a65073a3bcf0eb216b2a576","user",178),
  (21,"commonhuman_","lab@commonhuman.example","fcf1eed8596699624167416a1e7e122e","moderator",1337);
