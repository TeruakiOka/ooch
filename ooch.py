#! /usr/bin/python3
# encoding: utf8

import re
import mojimoji
import unicodedata as ud
import argparse

# 半角アルファベット全角変換用リスト
han_alphabet_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# 半角記号全角記号置換用辞書
mark_trans_han2zen_dic = {}
for (k, v) in zip('!"#$%&\'()*+,./:;<=>?@[¥]^_`{|}｡､･｢｣',
                  '！”＃＄％＆’（）＊＋，．／：；＜＝＞？＠［￥］＾＿｀｛｜｝。、・「」'):
    mark_trans_han2zen_dic[k] = v


def normalize(sentence, dupdel=False):

    if not sentence:
        return sentence

    ########################
    # 1文字になっている文字を複数文字に置換
    #     ㌫ => パーセント
    #     ⓾ => １０
    #     ㈱ => （株）
    ########################
    tmp_sentence = []
    for c in sentence:
        c_name = ud.name(c)

        # ⓱ ⓾ ❶ みたいなのの処理（①に丸める）
        new_c_name = None
        if c_name.startswith('NEGATIVE CIRCLED NUMBER'):
            new_c_name = c_name.replace('NEGATIVE ', '')
        elif c_name.startswith('NEGATIVE CIRCLED DIGIT'):
            new_c_name = c_name.replace('NEGATIVE ', '')
        elif c_name.startswith('DOUBLE CIRCLED DIGIT'):
            new_c_name = c_name.replace('DOUBLE ', '')
        elif c_name.startswith('DOUBLE CIRCLED NUMBER '):
            new_c_name = c_name.replace('DOUBLE ', '')
        elif c_name.startswith('DINGBAT NEGATIVE CIRCLED DIGIT '):
            new_c_name = c_name.replace('DINGBAT NEGATIVE ', '')
        elif c_name.startswith('DINGBAT NEGATIVE CIRCLED NUMBER '):
            new_c_name = c_name.replace('DINGBAT NEGATIVE ', '')
        elif c_name.startswith('WHITE '):
            new_c_name = c_name.replace('WHITE ', 'BLACK ')
        elif 'LEFTWARDS' in c_name:
            new_c_name = 'LEFTWARDS ARROW'
        elif 'UPWARDS' in c_name:
            new_c_name = 'UPWARDS ARROW'
        elif 'RIGHTWARDS' in c_name:
            new_c_name = 'RIGHTWARDS ARROW'
        elif 'DOWNWARDS' in c_name:
            new_c_name = 'DOWNWARDS ARROW'
        elif 'LEFT RIGHT' in c_name:
            new_c_name = 'LEFT RIGHT ARROW'

        if new_c_name is not None:
            try:
                ud.lookup(new_c_name)
            except KeyError:
                pass
            else:
                c_name = new_c_name
                c = ud.lookup(c_name)
        # ㌫ ⑰ ① ㈱ ・・・の処理
        if (c_name.startswith('SQUARE ')) or \
                (c_name.startswith('CIRCLED NUMBER')) or \
                (c_name.startswith('CIRCLED DIGIT')) or \
                (c_name.startswith('PARENTHESIZED IDEOGRAPH')) or \
                (c_name.startswith('CIRCLED IDEOGRAPH')) or \
                (c_name.startswith('VULGAR FRACTION')) or \
                ('EXCLAMATION' in c_name) or \
                ('QUESTION' in c_name) or \
                ('ROMAN NUMERAL' in c_name):
            c = ud.normalize('NFKC', c)
        tmp_sentence.append(c)
    sentence = ''.join(tmp_sentence)

    ########################
    # KATAKANA - HIRAGANA DOUBLE HYPHEN を 全角イコールに
    # 半→全以外のパターン
    ########################
    sentence = sentence.replace('゠', '＝')
    sentence = sentence.replace('№', 'Ｎｏ．')
    sentence = sentence.replace('℡', 'ＴＥＬ')
    sentence = sentence.replace('﹆', '、')
    sentence = sentence.replace('⁄', '／')
    sentence = sentence.replace('·', '・')
    sentence = sentence.replace('•', '・')
    sentence = sentence.replace('◦', '・')
    sentence = sentence.replace('♯', '＃')
    sentence = sentence.replace('〈', '＜')
    sentence = sentence.replace('〉', '＞')
    sentence = sentence.replace('◯', '〇')
    sentence = sentence.replace('≪', '《')
    sentence = sentence.replace('»', '》')
    sentence = sentence.replace('≫', '》')
    sentence = sentence.replace('′', '’')

    ########################
    # 半角英数字は全角に置換
    #     0-9 => ０-９
    #     A-Z => Ａ-Ｚ
    #     a-z => ａ-ｚ
    ########################
    ## 数字
    sentence = mojimoji.han_to_zen(sentence, kana=False, digit=True, ascii=False)
    ## アルファベット
    tmp_ustring = ''
    for c in sentence:
        if c in han_alphabet_list:
            c = mojimoji.han_to_zen(c)
        tmp_ustring += c
    sentence = tmp_ustring

    ########################
    # 半角カタカナは全角に置換
    # 半角の濁音と半濁音の記号が1文字扱いになってるので気をつけること。
    # >>> print(len(mojimoji.han_to_zen('ﾊﾟ')))
    # 1
    # >>> print(len('ﾊﾟ'))
    # 2
    ########################
    sentence = mojimoji.han_to_zen(sentence, kana=True, digit=False, ascii=False)

    ########################
    # 濁点・半濁点付与
    ########################
    tmp_sentence = [sentence[0]]
    dakuten = ud.normalize('NFD', 'だ')[1]
    han_dakuten = ud.normalize('NFD', 'ぱ')[1]
    for i, c in enumerate(sentence):
        if i == 0:
            continue
        old_c = c
        if c == '゜':
            c = han_dakuten
        elif c == '゛':
            c = dakuten
        if c != old_c:
            last_letter = tmp_sentence[-1]
            if len(ud.normalize('NFC', last_letter + c)) == 1:
                tmp_sentence[-1] = ud.normalize('NFC', last_letter + c)
                continue
        tmp_sentence.append(old_c)
    sentence = ''.join(tmp_sentence)

    ########################
    # NFC正規化
    # 平仮名濁点半濁点の正規化
    ########################
    sentence = ud.normalize('NFC', sentence)

    ########################
    # ハイフンマイナスっぽい文字を置換
    #
    # 以下はハイフンマイナスに置換する。
    #
    #     MODIFIER LETTER MINUS SIGN(U+02D7)
    #     ARMENIAN HYPHEN(U+058A)
    #     ハイフン(U+2010)
    #     ノンブレーキングハイフン(U+2011)
    #     フィギュアダッシュ(U+2012)
    #     エヌダッシュ(U+2013)
    #     Hyphen bullet(U+2043)
    #     上付きマイナス(U+207B)
    #     下付きマイナス(U+208B)
    #     負符号(U+2212)
    #     SOFT HYPHEN	U+00AD
    #     ……
    ########################
    sentence = re.sub('[˗֊‐‑‒–⁃⁻₋−\u00ad]', '-', sentence)

    ########################
    # 長音記号っぽい文字を置換
    #
    # 以下は全角長音記号に置換する。
    #
    #     エムダッシュ(U+2014)
    #     ホリゾンタルバー(U+2015)
    #     横細罫線(U+2500)
    #     横太罫線(U+2501)
    #     SMALL HYPHEN-MINUS(U+FE63)
    #     全角ハイフンマイナス(U+FF0D)
    #     半角長音記号(U+FF70)
    #
    ########################
    sentence = re.sub('[﹣－ｰ—―─━ー]', 'ー', sentence)  # normalize choonpus

    ########################
    # 1回以上連続する長音記号は1回に置換
    #
    # 連続したら削除する。
    #
    #     スーーーーーーパーーーーーー => スーパー
    ########################
    if dupdel:
        sentence = re.sub('ー+', 'ー', sentence)

    ########################
    #
    # チルダっぽい文字は全角チルダに置換
    #
    #
    #     半角チルダ
    #     チルダ演算子
    #     INVERTED LAZY S
    #     波ダッシュ
    #     WAVY DASH
    #     
    #
    ########################
    sentence = re.sub('[~∼∾〜〰～]', '～', sentence)

    ########################
    # 1回以上連続する全角チルダは1回に置換
    #
    # 連続したら削除する。
    #
    #     ス～～～～～パ～～～～～ => ス～パ～
    ########################
    if dupdel:
        sentence = re.sub('～+', '～', sentence)

    ########################
    # 以下の半角記号は全角記号に置換
    #
    #     !"#$%&\'()*+,./:;<=>?@[¥]^_`{|}｡､･｢｣
    #
    ########################
    tmp_ustring = ''
    for c in sentence:
        if c in mark_trans_han2zen_dic:
            c = mark_trans_han2zen_dic[c]
        tmp_ustring += c
    sentence = tmp_ustring

    ########################
    # 半角スペース、タブは全角スペースに置換
    #
    #     ' ' => '　'
    ########################
    sentence = sentence.replace(' ', '　')
    sentence = sentence.replace('\t', '　')

    ########################
    # 1つ以上の全角スペースは、1つの全角スペースに置換
    #
    #     ' ' => ' '
    ########################
    if dupdel:
        sentence = re.sub('[　]+', '　', sentence)

    return sentence


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Text normalizer for UniDic')
    parser.add_argument('-i', '--input', required=True, help='input file(.txt)')
    parser.add_argument('-o', '--output', required=True, help='output file(.txt)')
    parser.add_argument('--dupdel', action='store_true', help='Remove duplicated characters.(ー～　)')
    args = parser.parse_args()

    text = []
    with open(args.input, 'r', encoding='utf8') as fin:
        for line in fin:
            line = line.lstrip('\ufeff\ufffe')
            line = line.rstrip('\r\n')
            text.append(normalize(line, args.dupdel))
    
    with open(args.output, 'w', encoding='utf8') as fout:
        fout.write('\n'.join(text))

