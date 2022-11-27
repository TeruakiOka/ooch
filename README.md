# ooch

文字列正規化コード

NFKC正規化や[neologd](https://github.com/neologd/mecab-ipadic-neologd)の正規化コード（[Regexp.ja](https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja)や[neologdn](https://github.com/ikegami-yukino/neologdn)）に似ていますが、一番の違いはUniDicベースで英数字は全角にする点です。

外部モジュールは半角全角変換に[mojimoji](https://pypi.org/project/mojimoji/)を利用。
