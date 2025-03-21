# -*- coding: utf-8 -*-
from clean_up_path import CleanUpPath
from inkex.tester import ComparisonMixin, TestCase
from inkex.tester.filters import CompareNumericFuzzy, CompareWithPathSpace
from inkex.tester.mock import Capture


class RemoveTrueDuplicatesTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [("--id=path_w_duplicates",)]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class RemoveClose2DuplicatesTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_line",
            "--minUse=True",
            "--minlength=0.1",
            "--minUseSub=True",
            "--minlengthSub=0.1",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class SimpleJoinLoopTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_simple_loop",
            "--joinEndSub=True",
            "--maxdistJoin=4",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class TwoCirclesDefaultTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [("--id=two_circles",)]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class SelfIntersectTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=self_intersect",
            "--joinEndSub=True",
            "--maxdistJoin=4",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class LoopCloseTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_oo",
            "--closeSub=True",
            "--maxdistClose=1",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class MixDuplicateTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_zmo",
            "--minUse=True",
            "--minlength=1",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class JoinRowTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_loops_and_row",
            "--closeSub=True",
            "--maxdistJoin=4",
            "--joinEndSub=True",
            "--maxdistClose=4",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class JoinRowNoReverseTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_loops_and_row",
            "--closeSub=True",
            "--maxdistClose=4",
            "--joinEndSub=True",
            "--maxdistJoin=4",
            "--allow_reverse=False",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class MixTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_mix",
            "--minUse=True",
            "--minlength=2",
            "--closeSub=True",
            "--maxdistClose=4",
            "--joinEndSub=True",
            "--maxdistJoin=4",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class MixStraightTest(ComparisonMixin, TestCase):
    effect_class = CleanUpPath
    comparisons = [
        (
            "--id=path_mix",
            "--joinEndSub=True",
            "--maxdistJoin=4",
            "--option_join=2",
        )
    ]
    compare_filters = [
        CompareWithPathSpace(),
        CompareNumericFuzzy(),
    ]
    compare_file = "svg/clean_up_path.svg"


class RaiseErrorsTest(TestCase):
    """Test errormsg on selecting not accepted elements."""

    def test_effect(self):
        """Test that error is presented when inkscape:path-effect selected."""
        args = [
            self.data_file("svg", "clean_up_path.svg"),
            "--id=ink_effect",
        ]
        ext = CleanUpPath()

        with Capture("stderr") as stderr:
            ext.run(args)
            self.assertIn(
                "inkscape:path-effect applied",
                stderr.getvalue(),
            )
