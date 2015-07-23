/// <reference path="typings/jquery/jquery.d.ts" />

$(document).ready(function () {

    $.getJSON("/_get_game/1", function (data) {
        var items = [];
        items.push("<li id=' p1 '>Player1 score:" + data.p1 + "</li>");
        items.push("<li id=' p1l '>Player1 list:" + data.p1_list + "</li>");
        items.push("<li id=' p2 '>Player2 score:" + data.p2 + "</li>");
        items.push("<li id=' p2l '>Player2 list:" + data.p2_list + "</li>");

        $("#word").val(data.letter);
        $("<ul/>", {
            "class": "my-new-list",
            html: items.join("")
        }).appendTo("body");
    });
});

