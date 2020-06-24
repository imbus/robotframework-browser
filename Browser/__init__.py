__version__ = "0.1.1"

import os

from robot.api import logger  # type: ignore
from robot.libraries.BuiltIn import BuiltIn  # type: ignore
from robotlibcore import DynamicCore  # type: ignore

from .keywords import Validation, Control, Input
from .playwright import Playwright


class Browser(DynamicCore):
    """Browser library is a web testing library for Robot Framework.

    This documents explains how to use keywords provided by the Browser
    library. For information about installation, support, and more, please
    visit the
    [https://github.com/MarketSquare/robotframework-playwright|project pages].
    For more information about Robot Framework, see http://robotframework.org.

    Browser library uses
    [https://github.com/microsoft/playwright|Playwright Node module]
    to automate [https://www.chromium.org/Home|Chromium],
    [https://www.mozilla.org/en-US/firefox/new/|Firefox]
    and [https://webkit.org/|WebKit] with a single library.

    == Table of contents ==

    %TOC%

    = Locating elements =

    All keywords in Browser library that need to interact with an element
    on a web page take an argument typically named ``selector`` that specifies
    how to find the element.

    == Locator syntax ==

    Browser library supports same selector strategies as the underlying
    Playwright node module: xpath, css, id and text. The strategy can either
    be explicitly specified with a prefix or the strategy can be implicit.

    === Implicit selector strategy ===
    == !!! THIS ISN'T IMPLEMENTED YET !!! ==

    The default selector strategy is `css`. If selector does not contain
    one of the know selector strategies, `css`, `xpath`, `id` or `text` it is
    assumed to contain css selector. Also `selectors` starting with `//`
    considered as xpath selectors.

    Examples:

    | `Click` | span > button | # Use css selector strategy the element.   |
    | `Click` | //span/button | # Use xpath selector strategy the element. |

    === Explicit selector strategy ===

    The explicit selector strategy is specified with a prefix using syntax
    ``strategy=value``. Spaces around the separator are ignored, so
    ``css=foo``, ``css= foo`` and ``css = foo`` are all equivalent.


    Selector strategies that are supported by default are listed in the table
    below.

    | = Strategy = |     = Match based on =     |         = Example =            |
    | css          | CSS selector.              | ``css=div#example``            |
    | xpath        | XPath expression.          | ``xpath=//div[@id="example"]`` |
    | text         | Browser text engine.    | ``text=Login``                 |
    """

    ROBOT_LIBRARY_VERSION = __version__
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_LISTENER: "Browser"
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    SUPPORTED_BROWSERS = ["chrome", "firefox", "webkit"]

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.playwright = Playwright(self.outputdir)
        libraries = [
            Validation(self.playwright),
            Control(self.playwright, self.SUPPORTED_BROWSERS, self.outputdir),
            Input(self.playwright),
        ]
        DynamicCore.__init__(self, libraries)

    @property
    def outputdir(self):
        return BuiltIn().get_variable_value("${OUTPUTDIR}")

    def _close(self):
        self.playwright.close()

    def run_keyword(self, name, args, kwargs):
        try:
            return DynamicCore.run_keyword(self, name, args, kwargs)
        except AssertionError as e:
            self.test_error()
            raise e

    def test_error(self):
        """Sends screenshot command to Playwright.

        Only works during testing since this uses robot's outputdir for output
        """
        on_failure_keyword = "take page screenshot"
        try:
            path = os.path.join(
                BuiltIn().get_variable_value("${OUTPUTDIR}"),
                BuiltIn().get_variable_value("${TEST NAME}").replace(" ", "_")
                + "_FAILURE_SCREENSHOT",
            ).replace("\\", "\\\\")
            logger.info(f"Running `{on_failure_keyword}` with arguments `{path}`")
            BuiltIn().run_keyword(on_failure_keyword, path)
        except Exception as err:
            logger.error(
                f"Keyword '{on_failure_keyword}' could not be run on failure: {err}"
            )
