import fileinput
import sqlite3
from itertools import izip

TABLE_SCHEMA = ('CREATE TABLE WordLemma('
                    "word TEXT, "
                    'lemma TEXT, '
                    'tag TEXT, '
                    'probability REAL, '
                    'PRIMARY KEY (word, lemma, tag)'
                    ');')

def get_connection():
    conn = sqlite3.connect('finalProject/bnc_word_lemma.db')
    conn.text_factory = str
    return conn

def parse_bnc_word_lemma():
    for line in fileinput.input('finalProject/bnc.word.lemma.pos.txt'):
        lemma, word, tag, count, total, prob = line.split()
        # data parsing
        lemma, word, tag, count, total, prob = lemma[1:-1], word[1:-1], tag[1:-1], float(count), float(total), float(prob)
        # ignore foreign word (tag = F)
        if tag == 'F': continue
        yield (word, lemma, tag, prob)

def init_word_lemma_db(word_lemmas):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS WordLemma;")
        # create table
        cur.execute(TABLE_SCHEMA)
        # insert data
        cur.executemany('INSERT INTO WordLemma VALUES (?,?,?,?)', word_lemmas)

def search_lemma(word):
    with get_connection() as conn:
        cur = conn.cursor()
        cmd = 'SELECT lemma FROM WordLemma WHERE word=? and tag="v" ORDER BY probability DESC;'
        for res in cur.execute(cmd, (word,)):
            return res[0]

def search_tag(word):
    with get_connection() as conn:
        cur = conn.cursor()
        cmd = 'SELECT tag FROM WordLemma WHERE word=? ORDER BY probability DESC;'
        for res in cur.execute(cmd, (word,)):
            return res[0]

def bncTag(words):
    # print words
    tagged = [ str(search_tag(w.strip().lower())) for w in words ]
    return tagged

if __name__ == '__main__':
    # bnc word lemma data
    word_lemmas = list(parse_bnc_word_lemma())
    # insert data into sqlite3 db
    init_word_lemma_db(word_lemmas)
    # tag example
    words = 'This concert hall was too small to enter all of the audience .'.split()
    tagged = bncTag(words)
    print ' '.join('%s/%s' % wordTag for wordTag in izip(words, tagged))
