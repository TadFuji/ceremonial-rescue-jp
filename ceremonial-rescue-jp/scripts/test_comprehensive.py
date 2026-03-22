#!/usr/bin/env python3
"""Comprehensive test suite for ceremonial-rescue-jp skill scripts.

Tests amount_validator.py, ng_word_checker.py, and date_validator.py
with 50+ real-world scenarios covering all event types.

Usage:
    python test_comprehensive.py
"""
import json
import sys
import os

# Add parent scripts dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amount_validator import validate_amount  # noqa: E402
from ng_word_checker import check_text  # noqa: E402
from date_validator import validate_date  # noqa: E402

# ══════════════════════════════════════════════════
# Test tracking
# ══════════════════════════════════════════════════
total = 0
passed = 0
failed = 0
results = []


def test(test_id, description, category, func, expected_check, *args, **kwargs):
    """Run a single test and record result."""
    global total, passed, failed
    total += 1
    try:
        result = func(*args, **kwargs)
        ok = expected_check(result)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        results.append({
            "id": test_id,
            "category": category,
            "description": description,
            "status": status,
            "result_summary": summarize(result),
        })
    except Exception as e:
        failed += 1
        results.append({
            "id": test_id,
            "category": category,
            "description": description,
            "status": "ERROR",
            "result_summary": str(e),
        })


def summarize(result):
    """Create a brief summary of a result dict."""
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
# Category A: 葬儀（Funeral）金額バリデーション (10 tests)
# ══════════════════════════════════════════════════

print("=" * 60)
print("Category A: 葬儀 — 金額バリデーション")
print("=" * 60)

# A01: 同僚の親が亡くなった（5,000円）→ 相場内、OK
test("A01", "同僚の親の葬儀に5,000円（相場内）", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     5000, "funeral", "colleague", "parent")

# A02: 友人本人が亡くなった（10,000円）→ 相場上限、OK
test("A02", "友人本人の葬儀に10,000円（相場上限）", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     10000, "funeral", "friend", "self")

# A03: 親族の親が亡くなった（50,000円）→ 相場内、OK
test("A03", "親族（兄弟の親＝自分の親）に50,000円", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     50000, "funeral", "relative", "parent")

# A04: 40,000円 → 偶数+4を含む → NG
test("A04", "葬儀に40,000円（偶数+4含む）→NG", "葬儀/金額",
     validate_amount, lambda r: not r["passed"] and len(r["errors"]) >= 2,
     40000, "funeral", "colleague", "parent")

# A05: 9,000円 → 9を含む → NG
test("A05", "葬儀に9,000円（9含む）→NG", "葬儀/金額",
     validate_amount, lambda r: not r["passed"] and any(e["code"] == "CONTAINS_NINE" for e in r["errors"]),
     9000, "funeral", "friend", "self")

# A06: 取引先本人（30,000円）→ 相場内
test("A06", "取引先本人の葬儀に30,000円（相場内）", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     30000, "funeral", "client", "self")

# A07: 同僚の祖父母（3,000円）→ 相場内
test("A07", "同僚の祖父母の葬儀に3,000円（相場下限）", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     3000, "funeral", "colleague", "grandparent")

# A08: 新札チェック → 弔事は新札NG
test("A08", "弔事の新札アドバイスが出る", "葬儀/金額",
     validate_amount, lambda r: "新札は避けて" in r["bill_note"],
     5000, "funeral")

# A09: 親族の兄弟（30,000円）→ 相場内
test("A09", "親族（兄弟）の葬儀に30,000円", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     30000, "funeral", "relative", "sibling")

# A10: 相場より低い（同僚の親に1,000円）→ BELOW_RANGE警告
test("A10", "同僚の親の葬儀に1,000円（相場以下）→警告", "葬儀/金額",
     validate_amount, lambda r: r["passed"] and any(w["code"] == "BELOW_RANGE" for w in r["warnings"]),
     1000, "funeral", "colleague", "parent")

# ══════════════════════════════════════════════════
# Category B: 結婚式（Wedding）金額バリデーション (8 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category B: 結婚式 — 金額バリデーション")
print("=" * 60)

# B01: 友人の結婚式（30,000円）→ 相場ど真ん中
test("B01", "友人の結婚式に30,000円（相場ど真ん中）", "結婚式/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     30000, "wedding", "friend", "self")

# B02: 上司の結婚式（50,000円）→ 相場内
test("B02", "上司の結婚式に50,000円（相場上限）", "結婚式/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     50000, "wedding", "boss", "self")

# B03: 20,000円 → 偶数警告（近年許容）
test("B03", "結婚式に20,000円（偶数だが近年許容）→警告", "結婚式/金額",
     validate_amount, lambda r: r["passed"] and any(w["code"] == "EVEN_NUMBER_WEDDING_20K" for w in r["warnings"]),
     20000, "wedding", "colleague", "self")

# B04: 新札チェック → 慶事は新札を
test("B04", "慶事の新札アドバイスが出る", "結婚式/金額",
     validate_amount, lambda r: "新札を用意" in r["bill_note"],
     30000, "wedding")

# B05: 兄弟姉妹の結婚式（100,000円）→ 相場上限だが10万=偶数
test("B05", "兄弟の結婚式に100,000円（10万=偶数→NG, ただし相場内）", "結婚式/金額",
     validate_amount, lambda r: not r["passed"] and r["range_check"]["in_range"] and any(e["code"] == "EVEN_NUMBER" for e in r["errors"]),
     100000, "wedding", "relative", "sibling")

# B06: 40,000円 → 偶数+4含む → NG
test("B06", "結婚式に40,000円（偶数+4含む）→NG", "結婚式/金額",
     validate_amount, lambda r: not r["passed"] and len(r["errors"]) >= 2,
     40000, "wedding", "friend", "self")

# B07: 親族のいとこ（50,000円）→ 相場上限
test("B07", "いとこの結婚式に50,000円", "結婚式/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     50000, "wedding", "relative", "cousin")

# B08: 取引先の結婚式（30,000円）→ 相場
test("B08", "取引先の結婚式に30,000円", "結婚式/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     30000, "wedding", "client", "self")

# ══════════════════════════════════════════════════
# Category C: 季節行事・お祝い金額バリデーション (10 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category C: 季節行事・お祝い — 金額バリデーション")
print("=" * 60)

# C01: お中元（上司に5,000円）→ 相場上限
test("C01", "お中元で上司に5,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     5000, "gift", "ochugen", "boss")

# C02: お歳暮（取引先に10,000円）→ 相場上限
test("C02", "お歳暮で取引先に10,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     10000, "gift", "oseibo", "client")

# C03: 入学祝い（孫に30,000円）→ 相場内
test("C03", "入学祝いで孫に30,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     30000, "gift", "school_entry", "grandchild")

# C04: 七五三（甥姪に5,000円）→ 相場内
test("C04", "七五三で甥に5,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     5000, "gift", "shichigosan", "nephew_niece")

# C05: 還暦（親に30,000円）→ 相場内
test("C05", "還暦祝いで親に30,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     30000, "gift", "kanreki", "parent")

# C06: 快気祝いのお返し（3,000円）→ 相場内
test("C06", "快気祝いのお返し3,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     3000, "gift", "kaiki", "return")

# C07: お中元（仲人に10,000円）→ 相場上限
test("C07", "お中元で仲人に10,000円（相場上限）", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     10000, "gift", "ochugen", "matchmaker")

# C08: 入学祝い（友人の子に40,000円）→ 偶数+4 → NG
test("C08", "入学祝いで友人の子に40,000円（偶数+4）→NG", "季節/金額",
     validate_amount, lambda r: not r["passed"],
     40000, "gift", "school_entry", "friend_child")

# C09: 還暦（上司に5,000円）→ 相場内
test("C09", "還暦祝いで上司に5,000円", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     5000, "gift", "kanreki", "boss")

# C10: お歳暮（同僚に3,000円）→ 相場内
test("C10", "お歳暮で同僚に3,000円（相場下限）", "季節/金額",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     3000, "gift", "oseibo", "colleague")

# ══════════════════════════════════════════════════
# Category D: NGワードチェック — 弔事 (8 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category D: NGワードチェック — 弔事")
print("=" * 60)

# D01: 重ね言葉（重ね重ね）
test("D01", "弔事で「重ね重ね」→NG検出", "弔事/NG",
     check_text, lambda r: not r["passed"] and r["total_findings"] >= 1,
     "重ね重ねお悔やみ申し上げます", "funeral")

# D02: 直接的な死の表現（死ぬ）
test("D02", "弔事で「死んだ」→NG検出", "弔事/NG",
     check_text, lambda r: not r["passed"] and any(f["word"] == "死んだ" for f in r["findings"]),
     "突然死んだと聞いて驚きました", "funeral")

# D03: たびたび
test("D03", "弔事で「たびたび」→NG検出", "弔事/NG",
     check_text, lambda r: not r["passed"],
     "たびたびお世話になりました", "funeral")

# D04: 正常な弔辞 → パス
test("D04", "正常な弔辞文はNG検出なし", "弔事/NG",
     check_text, lambda r: r["passed"],
     "このたびは誠にご愁傷さまでございます。心よりお悔やみ申し上げます", "funeral")

# D05: 浄土真宗で「ご冥福」→ 宗派NG
test("D05", "浄土真宗で「ご冥福」→宗派NG", "弔事/NG",
     check_text, lambda r: not r["passed"] and any(f["category"] == "sect:浄土真宗" for f in r["findings"]),
     "ご冥福をお祈りいたします", "funeral", "浄土真宗")

# D06: 神式で「御仏前」→ 宗派NG
test("D06", "神式で「御仏前」→宗派NG", "弔事/NG",
     check_text, lambda r: not r["passed"] and any(f["category"] == "sect:神式" for f in r["findings"]),
     "御仏前にお供えします", "funeral", "神式")

# D07: キリスト教で「成仏」→ 宗派NG
test("D07", "キリスト教で「成仏」→宗派NG", "弔事/NG",
     check_text, lambda r: not r["passed"] and any(f["category"] == "sect:キリスト教" for f in r["findings"]),
     "安らかに成仏されますように", "funeral", "キリスト教")

# D08: 複数NGが同時に検出される
test("D08", "複数NG同時検出（重ね重ね+たびたび+死亡）", "弔事/NG",
     check_text, lambda r: not r["passed"] and r["total_findings"] >= 3,
     "重ね重ね申し訳ございません。たびたびご連絡いただいたのに、急な死亡の知らせに言葉もありません", "funeral")

# ══════════════════════════════════════════════════
# Category E: NGワードチェック — 慶事 (6 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category E: NGワードチェック — 慶事")
print("=" * 60)

# E01: 「別れる」→ NG
test("E01", "結婚式で「別れる」→NG検出", "慶事/NG",
     check_text, lambda r: not r["passed"],
     "二人が別れることなく末永くお幸せに", "wedding")

# E02: 「終わり」→ NG（お開き推奨）
test("E02", "結婚式で「終わり」→NG（お開き推奨）", "慶事/NG",
     check_text, lambda r: not r["passed"] and any(f["alternative"] == "お開き" for f in r["findings"]),
     "宴の終わりまで楽しませていただきました", "wedding")

# E03: 「切れる」「壊れる」→ NG
test("E03", "結婚式で「切れる」「壊れる」→NG", "慶事/NG",
     check_text, lambda r: not r["passed"] and r["total_findings"] >= 2,
     "絆が切れることなく、関係が壊れることのない日々を", "wedding")

# E04: 正常な祝辞 → パス
test("E04", "正常な祝辞はNG検出なし", "慶事/NG",
     check_text, lambda r: r["passed"],
     "ご結婚おめでとうございます。お二人の末永いお幸せをお祈りいたします", "wedding")

# E05: 「再び」→ NG（再婚連想）
test("E05", "結婚式で「再び」→NG（再婚連想）", "慶事/NG",
     check_text, lambda r: not r["passed"],
     "再びこのような素晴らしい日を迎えられて", "wedding")

# E06: 重ね言葉は結婚式でもNG
test("E06", "結婚式で「いよいよ」「ますます」→NG", "慶事/NG",
     check_text, lambda r: not r["passed"] and r["total_findings"] >= 2,
     "いよいよ結婚ですね。ますますお幸せに", "wedding")

# ══════════════════════════════════════════════════
# Category F: NGワードチェック — お祝い（celebration） (6 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category F: NGワードチェック — お祝い（celebration）")
print("=" * 60)

# F01: 快気祝いで「病気」→ NG
test("F01", "快気祝いで「病気」→NG", "お祝い/NG",
     check_text, lambda r: not r["passed"],
     "病気が治ってよかったですね", "celebration")

# F02: 快気祝いで「入院」「再発」→ NG
test("F02", "快気祝いで「入院」「再発」→NG", "お祝い/NG",
     check_text, lambda r: not r["passed"] and r["total_findings"] >= 2,
     "入院中は大変でしたね。再発しないことを祈ります", "celebration")

# F03: 快気祝いで「長引く」→ NG
test("F03", "快気祝いで「長引く」→NG", "お祝い/NG",
     check_text, lambda r: not r["passed"],
     "治療が長引くことなく回復されて安心しました", "celebration")

# F04: お祝いで重ね言葉 → NG
test("F04", "お祝いで「重ね重ね」→NG", "お祝い/NG",
     check_text, lambda r: not r["passed"],
     "重ね重ねお祝い申し上げます", "celebration")

# F05: 正常な快気祝いメッセージ → パス
test("F05", "正常な快気祝いメッセージはNG検出なし", "お祝い/NG",
     check_text, lambda r: r["passed"],
     "お元気になられて何よりです。ささやかですがお礼の品をお送りいたします", "celebration")

# F06: 正常な入学祝い → パス
test("F06", "正常な入学祝いメッセージはNG検出なし", "お祝い/NG",
     check_text, lambda r: r["passed"],
     "ご入学おめでとうございます。新しい門出を心よりお祝い申し上げます", "celebration")

# ══════════════════════════════════════════════════
# Category G: 日付・六曜バリデーション (6 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category G: 日付・六曜バリデーション")
print("=" * 60)

# G01: 日付フォーマットエラー
test("G01", "不正な日付フォーマット→エラー", "日付",
     validate_date, lambda r: "error" in r,
     "2026/04/15", "funeral")

# G02: 正常な日付 → 六曜が返る
test("G02", "正常な日付で六曜が返る", "日付",
     validate_date, lambda r: "rokuyo" in r and r["rokuyo"] in ["大安", "赤口", "先勝", "友引", "先負", "仏滅"],
     "2026-04-15", "funeral")

# G03: 結婚式で大安 → 推奨
# Find a 大安 date: (month + day) % 6 == 0 → e.g. month=6, day=6 → (6+6)%6=0 → 大安
test("G03", "結婚式で大安→推奨コメント", "日付",
     validate_date, lambda r: r["rokuyo"] == "大安" and len(r.get("recommendations", [])) > 0,
     "2026-06-06", "wedding")

# G04: 曜日が正しく表示される
test("G04", "曜日が正しく返る", "日付",
     validate_date, lambda r: "weekday" in r and "曜日" in r["weekday"],
     "2026-04-01", "wedding")

# G05: 友引の日に葬儀 → エラー
# (month + day) % 6 == 3 → 友引。 month=1, day=2 → (1+2)%6=3 → 友引
test("G05", "友引に葬儀→エラー警告", "日付",
     validate_date, lambda r: r["rokuyo"] == "友引" and not r["passed"],
     "2026-01-02", "funeral")

# G06: 仏滅の日に結婚式 → 警告
# (month + day) % 6 == 5 → 仏滅。 month=1, day=5 → (1+5)%6=0 → 大安... try month=2, day=3 → (2+3)%6=5 → 仏滅
test("G06", "仏滅に結婚式→警告", "日付",
     validate_date, lambda r: r["rokuyo"] == "仏滅" and len(r.get("warnings", [])) > 0,
     "2026-02-03", "wedding")

# ══════════════════════════════════════════════════
# Category H: エッジケース・境界値テスト (8 tests)
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category H: エッジケース・境界値テスト")
print("=" * 60)

# H01: 金額0円
test("H01", "金額0円→passed（エラーなし、ただし常識外）", "エッジ",
     validate_amount, lambda r: r["passed"],  # No 4/9/even check triggers
     0, "funeral")

# H02: 非常に高額（1,000,000円）
test("H02", "100万円→偶数チェック", "エッジ",
     validate_amount, lambda r: not r["passed"],  # 1000000 → even
     1000000, "funeral")

# H03: 3,000円はOK（奇数、4/9なし）
test("H03", "3,000円→OK（奇数、4/9なし）", "エッジ",
     validate_amount, lambda r: r["passed"],
     3000, "funeral")

# H04: allタイプでNG検出
test("H04", "allタイプで弔事+慶事+お祝いNG全検出", "エッジ",
     check_text, lambda r: not r["passed"] and r["total_findings"] >= 2,
     "死亡のお知らせに別れの悲しみを感じ、病気の辛さを思います", "all")

# H05: 空文字列チェック
test("H05", "空文字列→NGなし（passed）", "エッジ",
     check_text, lambda r: r["passed"],
     "", "funeral")

# H06: giftタイプの新札アドバイス
test("H06", "giftタイプで新札アドバイス", "エッジ",
     validate_amount, lambda r: "新札を用意" in r["bill_note"],
     5000, "gift")

# H07: 相場範囲外（お中元で上司に50,000円）→ ABOVE_RANGE
test("H07", "お中元で上司に50,000円→相場超過警告", "エッジ",
     validate_amount, lambda r: any(w["code"] == "ABOVE_RANGE" for w in r["warnings"]),
     50000, "gift", "ochugen", "boss")

# H08: 存在しないrelationship/target組み合わせ → range_check = None
test("H08", "存在しない関係性→range_checkなし", "エッジ",
     validate_amount, lambda r: r["range_check"] is None,
     5000, "gift", "unknown_rel", "unknown_target")

# ══════════════════════════════════════════════════
# Category I: 実際のユーザープロンプトシミュレーション (6 tests)
# これらはスキルのワークフロー全体を模擬的にテスト
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Category I: 実際のプロンプト向けバリデーション組み合わせテスト")
print("=" * 60)

# I01: 「同僚の父の通夜に参列。5,000円を包みたい」
# → 金額OK + メッセージNG検出なし
test("I01", "同僚の父の通夜に5,000円+正常メッセージ → 金額OK", "統合",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     5000, "funeral", "colleague", "parent")

# I02: 同上のメッセージをNG検出
test("I02", "同僚の父の通夜向けメッセージ → NGなし", "統合",
     check_text, lambda r: r["passed"],
     "このたびはご愁傷さまでございます。心よりお悔やみ申し上げます。", "funeral")

# I03: 「友人の結婚式でスピーチ。祝辞をチェックして」
test("I03", "結婚式スピーチ原稿のNGチェック → NGあり（終わり）", "統合",
     check_text, lambda r: not r["passed"],
     "新郎新婦の素晴らしい門出に立ち会えて光栄です。パーティーの終わりまで楽しみましょう。", "wedding")

# I04: 「上司が還暦。10,000円でいい？」
test("I04", "上司の還暦に10,000円 → 相場上限", "統合",
     validate_amount, lambda r: r["passed"] and r["range_check"]["in_range"],
     10000, "gift", "kanreki", "boss")

# I05: 「快気祝いのメッセージ書いた。チェックして」
test("I05", "快気祝いの問題あるメッセージ → NG検出", "統合",
     check_text, lambda r: not r["passed"],
     "入院中はお見舞いいただきありがとうございました。おかげさまで病気も治り、再び元気になりました。", "celebration")

# I06: 「甥の入学祝い。大学入学で20,000円？」
test("I06", "大学入学の甥に20,000円 → 偶数チェック", "統合",
     validate_amount, lambda r: not r["passed"],
     20000, "gift", "school_entry", "nephew_niece")

# ══════════════════════════════════════════════════
# Results Summary
# ══════════════════════════════════════════════════
print("\n" + "=" * 60)
print(f"RESULTS SUMMARY: {passed}/{total} passed, {failed} failed")
print("=" * 60)

for r in results:
    icon = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "💥"
    print(f"  {icon} [{r['id']}] {r['description']}")
    if r["status"] != "PASS":
        print(f"       → {r['result_summary']}")

print(f"\n{'=' * 60}")
print(f"TOTAL: {total} tests | PASS: {passed} | FAIL: {failed}")
print(f"{'=' * 60}")

# Output JSON results for analysis
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed / total * 100:.1f}%",
        "results": results,
    }, f, ensure_ascii=False, indent=2)

print(f"\nJSON results saved to: {output_path}")
sys.exit(0 if failed == 0 else 1)
