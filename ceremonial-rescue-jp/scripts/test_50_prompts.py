#!/usr/bin/env python3
"""Real-world prompt simulation test for ceremonial-rescue-jp skill (v3 hybrid).

Simulates 50 realistic user prompts and validates:
- Event classification → correct script parameters
- Amount validation → expected pass/fail
- NG word checking → expected detection
- Date validation → expected rokuyō warnings
- References loading → files exist and contain expected content

Usage:
    python test_50_prompts.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amount_validator import validate_amount
from ng_word_checker import check_text
from date_validator import validate_date

# ══════════════════════════════════════════════════
# Test infrastructure
# ══════════════════════════════════════════════════
total = 0
passed = 0
failed = 0
results = []

def test(test_id, prompt, category, checks):
    """Run multiple checks for a single user prompt scenario."""
    global total, passed, failed
    all_ok = True
    check_details = []

    for check in checks:
        total += 1
        try:
            result = check["func"](*check["args"], **check.get("kwargs", {}))
            ok = check["expect"](result)
            if ok:
                passed += 1
            else:
                failed += 1
                all_ok = False
            check_details.append({
                "check": check["desc"],
                "status": "PASS" if ok else "FAIL",
                "detail": summarize(result),
            })
        except Exception as e:
            failed += 1
            all_ok = False
            check_details.append({
                "check": check["desc"],
                "status": "ERROR",
                "detail": str(e),
            })

    icon = "✅" if all_ok else "❌"
    print(f"  {icon} [{test_id}] {prompt[:60]}...")
    for cd in check_details:
        sub_icon = "  ✓" if cd["status"] == "PASS" else "  ✗"
        if cd["status"] != "PASS":
            print(f"       {sub_icon} {cd['check']}: {cd['detail']}")

    results.append({
        "id": test_id,
        "prompt": prompt,
        "category": category,
        "all_passed": all_ok,
        "checks": check_details,
    })

def summarize(result):
    if "passed" in result:
        s = f"passed={result['passed']}"
        if "total_findings" in result:
            s += f", findings={result['total_findings']}"
        if "errors" in result and isinstance(result["errors"], list):
            codes = [e["code"] for e in result["errors"]]
            if codes:
                s += f", errors={codes}"
        if "warnings" in result and isinstance(result["warnings"], list):
            codes = [w["code"] for w in result["warnings"]]
            if codes:
                s += f", warnings={codes}"
        if "range_check" in result and result["range_check"]:
            s += f", in_range={result['range_check']['in_range']}"
        if "rokuyo" in result:
            s += f", rokuyo={result['rokuyo']}"
        return s
    return str(result)[:200]

# ══════════════════════════════════════════════════
# References file existence check
# ══════════════════════════════════════════════════
print("=" * 70)
print("Pre-check: references/ files exist and contain expected content")
print("=" * 70)

ref_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references")
ref_files = {
    "etiquette.md": ["のし袋", "焼香", "口頭セリフ", "招待状", "服装", "行動NG", "スピーチ", "地域差"],
    "company_mode.md": ["3層判断", "社内通知", "HR確認", "供花", "弔電"],
    "ng_words.md": ["重ね重ね", "浄土真宗", "ご冥福", "別れる", "病気", "再発"],
}

for fname, keywords in ref_files.items():
    fpath = os.path.join(ref_dir, fname)
    total += 1
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        missing = [kw for kw in keywords if kw not in content]
        if not missing:
            passed += 1
            print(f"  ✅ [REF] {fname} — OK ({len(keywords)} keywords found)")
            results.append({"id": f"REF-{fname}", "prompt": f"references/{fname}", "category": "references", "all_passed": True, "checks": []})
        else:
            failed += 1
            print(f"  ❌ [REF] {fname} — Missing keywords: {missing}")
            results.append({"id": f"REF-{fname}", "prompt": f"references/{fname}", "category": "references", "all_passed": False, "checks": [{"check": "keyword", "status": "FAIL", "detail": str(missing)}]})
    else:
        failed += 1
        print(f"  ❌ [REF] {fname} — FILE NOT FOUND")
        results.append({"id": f"REF-{fname}", "prompt": f"references/{fname}", "category": "references", "all_passed": False, "checks": [{"check": "exists", "status": "FAIL", "detail": "not found"}]})

# ══════════════════════════════════════════════════
# 50 Real-World Prompts
# ══════════════════════════════════════════════════
print("\n" + "=" * 70)
print("50 Real-World Prompt Tests")
print("=" * 70)

# --- 葬儀系 (P01-P10) ---
print("\n--- 葬儀系 (P01-P10) ---")

test("P01", "それほど仲は良くない、会社の同僚（男性27歳）が亡くなりました。通夜に参列します。", "葬儀",
     [{"desc": "金額5000円=同僚本人の相場内", "func": validate_amount, "args": (5000, "funeral", "colleague", "self"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "弔辞メッセージにNGなし", "func": check_text,
       "args": ("このたびは誠にご愁傷さまでございます。心よりお悔やみ申し上げます",), "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P02", "大切な友人のお父様がお亡くなりになりました。", "葬儀",
     [{"desc": "金額10000円=友人の親の相場上限", "func": validate_amount, "args": (10000, "funeral", "friend", "parent"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "弔辞にNGなし", "func": check_text,
       "args": ("突然のことで言葉もありません。何かできることがあればおっしゃってください",), "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P03", "上司のお母様がお亡くなりになりました。家族葬とのことです。", "葬儀",
     [{"desc": "メッセージにNGなし（家族葬なので参列不要）", "func": check_text,
       "args": ("このたびはご愁傷さまでございます。お力落としのないようにお過ごしください",), "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P04", "取引先の社長がお亡くなりになりました。会社として対応が必要です。", "葬儀/会社",
     [{"desc": "金額30000円=取引先本人の相場内", "func": validate_amount, "args": (30000, "funeral", "client", "self"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P05", "昨年亡くなった友人のことを最近知りました。何ができますか？", "葬儀/後日",
     [{"desc": "後日弔問メッセージにNGなし", "func": check_text,
       "args": ("ご連絡が遅くなり申し訳ございません。遅ればせながら心よりお悔やみ申し上げます",), "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P06", "祖母が亡くなりました。香典はいくら包めばいいですか？", "葬儀",
     [{"desc": "金額30000円=親族の祖父母の相場内", "func": validate_amount, "args": (30000, "funeral", "relative", "grandparent"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額40000円=偶数+4でNG", "func": validate_amount, "args": (40000, "funeral", "relative", "grandparent"),
       "expect": lambda r: not r["passed"]}])

test("P07", "兄が亡くなりました。金額はどのくらいが相場ですか？", "葬儀",
     [{"desc": "金額50000円=兄弟の相場上限", "func": validate_amount, "args": (50000, "funeral", "relative", "sibling"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P08", "近所の方がお亡くなりになりました。通夜は友引の日です。大丈夫ですか？", "葬儀/日付",
     [{"desc": "友引の葬儀は避けるべき", "func": validate_date, "args": ("2026-01-02", "funeral"),
       "expect": lambda r: r["rokuyo"] == "友引" and not r["passed"]}])

test("P09", "同僚のお祖父様が亡くなったのですが、「香典は辞退します」と言われました。", "葬儀/辞退",
     [{"desc": "メッセージにNGなし", "func": check_text,
       "args": ("このたびはご愁傷さまでございます。どうぞご無理なさらないようにお過ごしください",), "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P10", "浄土真宗の葬儀に参列します。気を付けることはありますか？", "葬儀/宗派",
     [{"desc": "「ご冥福」は浄土真宗NG", "func": check_text,
       "args": ("ご冥福をお祈りいたします",), "kwargs": {"event_type": "funeral", "sect": "浄土真宗"},
       "expect": lambda r: not r["passed"] and any(f["category"] == "sect:浄土真宗" for f in r["findings"])},
      {"desc": "「お悔やみ申し上げます」はOK", "func": check_text,
       "args": ("心よりお悔やみ申し上げます",), "kwargs": {"event_type": "funeral", "sect": "浄土真宗"},
       "expect": lambda r: r["passed"]}])

# --- 結婚式系 (P11-P20) ---
print("\n--- 結婚式系 (P11-P20) ---")

test("P11", "それほど仲は良くない、会社の同僚（男性27歳）が結婚することになりました。", "結婚式",
     [{"desc": "金額30000円=同僚の相場", "func": validate_amount, "args": (30000, "wedding", "colleague", "self"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "祝辞にNGなし", "func": check_text,
       "args": ("ご結婚おめでとうございます。末永いご多幸をお祈り申し上げます",), "kwargs": {"event_type": "wedding"},
       "expect": lambda r: r["passed"]}])

test("P12", "小学校の時の友達が結婚することになりました。披露宴に招待されました。服装で気を付けることは？", "結婚式/服装",
     [{"desc": "金額30000円=友人の相場", "func": validate_amount, "args": (30000, "wedding", "friend", "self"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P13", "部下が結婚します。ご祝儀はいくらが適切ですか？", "結婚式",
     [{"desc": "金額30000円=部下の相場下限", "func": validate_amount, "args": (30000, "wedding", "subordinate", "self"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額50000円=部下の相場上限", "func": validate_amount, "args": (50000, "wedding", "subordinate", "self"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P14", "いとこの結婚式に招待されました。30,000円で大丈夫ですか？", "結婚式",
     [{"desc": "金額30000円=いとこの相場下限", "func": validate_amount, "args": (30000, "wedding", "relative", "cousin"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P15", "友人の結婚式でスピーチを頼まれました。何分くらいが適切ですか？", "結婚式/スピーチ",
     [{"desc": "スピーチ原稿にNGなし", "func": check_text,
       "args": ("新郎の太郎さんとは大学時代からの親友です。太郎さんの誠実な人柄はご存知の通りです。お二人の末永いお幸せをお祈りいたします",),
       "kwargs": {"event_type": "wedding"},
       "expect": lambda r: r["passed"]}])

test("P16", "友人の結婚式に出席できません。ご祝儀はどうすればいいですか？", "結婚式/欠席",
     [{"desc": "金額30000円=友人の相場（欠席でも）", "func": validate_amount, "args": (30000, "wedding", "friend", "self"),
       "expect": lambda r: r["passed"]}])

test("P17", "20,000円のご祝儀はマナー違反ですか？", "結婚式/金額",
     [{"desc": "20000円=偶数だが近年許容→警告", "func": validate_amount, "args": (20000, "wedding", "colleague", "self"),
       "expect": lambda r: r["passed"] and any(w["code"] == "EVEN_NUMBER_WEDDING_20K" for w in r["warnings"])}])

test("P18", "結婚式に出す手紙に「終わりなき幸せを」と書きたいのですが。", "結婚式/NG",
     [{"desc": "「終わり」はNG検出", "func": check_text,
       "args": ("終わりなき幸せを二人で築いてください",), "kwargs": {"event_type": "wedding"},
       "expect": lambda r: not r["passed"] and any(f["word"] == "終わり" for f in r["findings"])}])

test("P19", "結婚式の日取りが仏滅なんですが、大丈夫でしょうか？", "結婚式/日付",
     [{"desc": "仏滅の結婚式=警告", "func": validate_date, "args": ("2026-02-03", "wedding"),
       "expect": lambda r: r["rokuyo"] == "仏滅" and len(r.get("warnings", [])) > 0}])

test("P20", "結婚する友人に「ますますお幸せに」とLINEで送りたいのですが。", "結婚式/NG",
     [{"desc": "「ますます」は結婚式でもNG（重ね言葉）", "func": check_text,
       "args": ("ますますお幸せにお過ごしください",), "kwargs": {"event_type": "wedding"},
       "expect": lambda r: not r["passed"] and any(f["word"] == "ますます" for f in r["findings"])}])

# --- お中元・お歳暮 (P21-P26) ---
print("\n--- お中元・お歳暮 (P21-P26) ---")

test("P21", "上司にお中元を贈りたいのですが、いくらくらいが相場ですか？", "お中元",
     [{"desc": "金額5000円=上司の相場上限", "func": validate_amount, "args": (5000, "gift", "ochugen", "boss"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P22", "取引先にお歳暮を送ります。金額の目安を教えてください。", "お歳暮",
     [{"desc": "金額5000円=取引先の相場内", "func": validate_amount, "args": (5000, "gift", "oseibo", "client"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額10000円=取引先の相場上限", "func": validate_amount, "args": (10000, "gift", "oseibo", "client"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P23", "お中元で同僚に3000円は安すぎますか？", "お中元",
     [{"desc": "金額3000円=同僚の相場下限", "func": validate_amount, "args": (3000, "gift", "ochugen", "colleague"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P24", "仲人さんへのお歳暮はいくらが適切ですか？", "お歳暮",
     [{"desc": "金額5000円=仲人の相場内", "func": validate_amount, "args": (5000, "gift", "oseibo", "matchmaker"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P25", "お中元の送り状を書きたいです。失礼のない文面を教えてください。", "お中元/文面",
     [{"desc": "送り状にNGなし", "func": check_text,
       "args": ("日頃より大変お世話になっております。ささやかではございますが、夏のご挨拶をお送りさせていただきます",),
       "kwargs": {"event_type": "celebration"},
       "expect": lambda r: r["passed"]}])

test("P26", "親戚にお中元を贈るのですが、4000円の品物でいいですか？", "お中元/金額NG",
     [{"desc": "金額4000円=4を含むのでNG", "func": validate_amount, "args": (4000, "gift", "ochugen", "relative"),
       "expect": lambda r: not r["passed"] and any(e["code"] == "CONTAINS_FOUR" for e in r["errors"])}])

# --- 年賀状・喪中 (P27-P30) ---
print("\n--- 年賀状・喪中 (P27-P30) ---")

test("P27", "身内に不幸がありました。年賀状を断りたいです。", "喪中",
     [{"desc": "喪中はがきメッセージにNGなし", "func": check_text,
       "args": ("喪中につき年末年始のご挨拶を失礼させていただきます。本年中に賜りましたご厚情に深く感謝申し上げます",),
       "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P28", "上司への年賀状の文面を考えてください。", "年賀状",
     [{"desc": "年賀状文面にNGなし", "func": check_text,
       "args": ("謹んで新春のお慶びを申し上げます。旧年中は格別のご指導を賜り厚く御礼申し上げます。本年もどうぞよろしくお願い申し上げます",),
       "kwargs": {"event_type": "celebration"},
       "expect": lambda r: r["passed"]}])

test("P29", "喪中の方に寒中見舞いを出したいのですが。", "寒中見舞い",
     [{"desc": "寒中見舞い文面にNGなし", "func": check_text,
       "args": ("寒中お見舞い申し上げます。ご服喪中と存じ年頭のご挨拶は控えさせていただきました。厳寒の折、どうぞご自愛ください",),
       "kwargs": {"event_type": "funeral"},
       "expect": lambda r: r["passed"]}])

test("P30", "喪中はがきはいつまでに出せばいいですか？", "喪中",
     [{"desc": "喪中はがきメッセージにNG混入テスト", "func": check_text,
       "args": ("重ね重ねのご無礼をお詫び申し上げます",), "kwargs": {"event_type": "funeral"},
       "expect": lambda r: not r["passed"] and any(f["word"] == "重ね重ね" for f in r["findings"])}])

# --- 快気祝い (P31-P34) ---
print("\n--- 快気祝い (P31-P34) ---")

test("P31", "入院していたのですが退院しました。お見舞いをくれた方にお返しをしたいです。", "快気祝い",
     [{"desc": "金額3000円=快気祝い相場内", "func": validate_amount, "args": (3000, "gift", "kaiki", "return"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "メッセージに「病気」はNG", "func": check_text,
       "args": ("病気が治りました。入院中はお見舞いありがとうございました",), "kwargs": {"event_type": "celebration"},
       "expect": lambda r: not r["passed"] and r["total_findings"] >= 2}])

test("P32", "快気祝いのメッセージで「再発しないように」と書いてもいいですか？", "快気祝い/NG",
     [{"desc": "「再発」はNG", "func": check_text,
       "args": ("再発しないよう気をつけてくださいね",), "kwargs": {"event_type": "celebration"},
       "expect": lambda r: not r["passed"] and any(f["word"] == "再発" for f in r["findings"])}])

test("P33", "快気祝いの正しいメッセージを教えてください。", "快気祝い",
     [{"desc": "正しいメッセージはNG検出なし", "func": check_text,
       "args": ("おかげさまで元気になりました。ご心配をおかけしました。ささやかですがお礼の品をお送りいたします",),
       "kwargs": {"event_type": "celebration"},
       "expect": lambda r: r["passed"]}])

test("P34", "快気祝いのお返しは5000円で大丈夫ですか？", "快気祝い",
     [{"desc": "金額5000円=快気祝い相場上限", "func": validate_amount, "args": (5000, "gift", "kaiki", "return"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

# --- 入学祝い (P35-P38) ---
print("\n--- 入学祝い (P35-P38) ---")

test("P35", "甥が小学校に入学します。お祝いを渡したいのですが。", "入学祝い",
     [{"desc": "金額10000円=甥の相場内", "func": validate_amount, "args": (10000, "gift", "school_entry", "nephew_niece"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P36", "孫が大学に入学します。いくら包めばいいですか？", "入学祝い",
     [{"desc": "金額30000円=孫の相場内", "func": validate_amount, "args": (30000, "gift", "school_entry", "grandchild"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額50000円=孫の相場上限", "func": validate_amount, "args": (50000, "gift", "school_entry", "grandchild"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P37", "友人の子供が中学に入学します。3000円は少ないですか？", "入学祝い",
     [{"desc": "金額3000円=友人の子の相場下限", "func": validate_amount, "args": (3000, "gift", "school_entry", "friend_child"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P38", "入学祝いのメッセージを考えてください。", "入学祝い/メッセージ",
     [{"desc": "入学祝いメッセージにNGなし", "func": check_text,
       "args": ("ご入学おめでとうございます。新しい学校生活が素晴らしいものになりますように。勉強も遊びも楽しんでくださいね",),
       "kwargs": {"event_type": "celebration"},
       "expect": lambda r: r["passed"]}])

# --- 七五三 (P39-P41) ---
print("\n--- 七五三 (P39-P41) ---")

test("P39", "めいっこが5歳になりました。何かしてあげたいです。", "七五三",
     [{"desc": "金額5000円=甥姪の相場内", "func": validate_amount, "args": (5000, "gift", "shichigosan", "nephew_niece"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P40", "孫の七五三にお祝いを渡したいです。相場はいくらですか？", "七五三",
     [{"desc": "金額10000円=孫の相場下限", "func": validate_amount, "args": (10000, "gift", "shichigosan", "grandchild"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額30000円=孫の相場上限", "func": validate_amount, "args": (30000, "gift", "shichigosan", "grandchild"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P41", "友人の子供の七五三にお祝いは必要ですか？", "七五三",
     [{"desc": "金額3000円=友人の子の相場下限", "func": validate_amount, "args": (3000, "gift", "shichigosan", "friend_child"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

# --- 還暦・長寿祝い (P42-P44) ---
print("\n--- 還暦・長寿祝い (P42-P44) ---")

test("P42", "父が還暦を迎えます。何を贈ればいいですか？", "還暦",
     [{"desc": "金額30000円=親の相場内", "func": validate_amount, "args": (30000, "gift", "kanreki", "parent"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P43", "上司が60歳になります。部署でお祝いをしたいです。", "還暦/会社",
     [{"desc": "金額5000円=上司の相場内", "func": validate_amount, "args": (5000, "gift", "kanreki", "boss"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額10000円=上司の相場上限", "func": validate_amount, "args": (10000, "gift", "kanreki", "boss"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

test("P44", "祖母が米寿（88歳）を迎えます。お祝いの相場は？", "米寿",
     [{"desc": "金額10000円=祖父母の相場下限", "func": validate_amount, "args": (10000, "gift", "kanreki", "grandparent"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]},
      {"desc": "金額30000円=祖父母の相場上限", "func": validate_amount, "args": (30000, "gift", "kanreki", "grandparent"),
       "expect": lambda r: r["passed"] and r["range_check"]["in_range"]}])

# --- 複合・エッジケース (P45-P50) ---
print("\n--- 複合・エッジケース (P45-P50) ---")

test("P45", "神式の葬儀に参列します。注意することは？", "葬儀/神式",
     [{"desc": "「御仏前」は神式でNG", "func": check_text,
       "args": ("御仏前にお供えさせていただきます",), "kwargs": {"event_type": "funeral", "sect": "神式"},
       "expect": lambda r: not r["passed"] and any(f["category"] == "sect:神式" for f in r["findings"])},
      {"desc": "「御玉串料」はOK", "func": check_text,
       "args": ("御玉串料をお供えさせていただきます",), "kwargs": {"event_type": "funeral", "sect": "神式"},
       "expect": lambda r: r["passed"]}])

test("P46", "キリスト教の葬儀に参列します。何を持っていけばいいですか？", "葬儀/キリスト教",
     [{"desc": "「成仏」はキリスト教でNG", "func": check_text,
       "args": ("安らかに成仏されますよう",), "kwargs": {"event_type": "funeral", "sect": "キリスト教"},
       "expect": lambda r: not r["passed"] and any(f["category"] == "sect:キリスト教" for f in r["findings"])}])

test("P47", "結婚式のスピーチで「いよいよ新生活が始まりますね」と言いたいのですが。", "結婚式/NG",
     [{"desc": "「いよいよ」は結婚式NG（重ね言葉）", "func": check_text,
       "args": ("いよいよ新生活が始まりますね",), "kwargs": {"event_type": "wedding"},
       "expect": lambda r: not r["passed"] and any(f["word"] == "いよいよ" for f in r["findings"])}])

test("P48", "大安の日に結婚式を予定しています。良い日取りですか？", "結婚式/日付",
     [{"desc": "大安の結婚式=推奨コメント", "func": validate_date, "args": ("2026-06-06", "wedding"),
       "expect": lambda r: r["rokuyo"] == "大安" and len(r.get("recommendations", [])) > 0}])

test("P49", "弔辞で「安らかにお眠りください」は浄土真宗でNGと聞きましたが本当ですか？", "葬儀/浄土真宗",
     [{"desc": "「安らかにお眠りください」は浄土真宗NG", "func": check_text,
       "args": ("安らかにお眠りください",), "kwargs": {"event_type": "funeral", "sect": "浄土真宗"},
       "expect": lambda r: not r["passed"]}])

test("P50", "弔事と慶事が重なった場合、どちらを優先すべきですか？", "複合",
     [{"desc": "弔事メッセージ+慶事メッセージのallチェック", "func": check_text,
       "args": ("死亡の知らせとお祝いが重なり、別れの悲しみと病気の回復を同時に感じています",), "kwargs": {"event_type": "all"},
       "expect": lambda r: not r["passed"] and r["total_findings"] >= 2}])

# ══════════════════════════════════════════════════
# Final Summary
# ══════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"RESULTS SUMMARY: {passed}/{total} passed, {failed} failed")
print("=" * 70)

failed_list = [r for r in results if not r["all_passed"]]
if failed_list:
    print("\n❌ Failed scenarios:")
    for r in failed_list:
        print(f"  [{r['id']}] {r['prompt'][:70]}")
        for c in r["checks"]:
            if c["status"] != "PASS":
                print(f"       ✗ {c['check']}: {c['detail']}")

print(f"\n{'=' * 70}")
print(f"TOTAL: {total} checks | PASS: {passed} | FAIL: {failed}")
print(f"{'=' * 70}")

# Save JSON
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_50_prompts_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed/total*100:.1f}%",
        "scenarios": len([r for r in results if r["category"] != "references"]),
        "results": results,
    }, f, ensure_ascii=False, indent=2)

print(f"\nJSON results saved to: {output_path}")
sys.exit(0 if failed == 0 else 1)
