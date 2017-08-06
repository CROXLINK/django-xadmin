/**
 * Select2 Chinese translation
 */
(function ($) {
    "use strict";
    $.extend($.fn.select2.defaults, {
        formatNoMatches: function () { return "没有找到符合項"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; return "請再輸入" + n + "個字元";},
        formatInputTooLong: function (input, max) { var n = input.length - max; return "請删掉" + n + "個字元";},
        formatSelectionTooBig: function (limit) { return "您只能選擇最多" + limit + "項"; },
        formatLoadMore: function (pageNumber) { return "讀入結果中..."; },
        formatSearching: function () { return "搜尋中..."; }
    });
})(jQuery);