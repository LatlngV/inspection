(function ($) {

    $.fn.BootSideMenu = function (options) {

        var oldCode, newCode, side;

        newCode = "";

        var settings = $.extend({
            side: "left",
            autoClose: true
        }, options);

        side = settings.side;
        autoClose = settings.autoClose;

        this.addClass("container sidebar_1");

        if (side === "left") {
            this.addClass("sidebar_1-left");
        } else if (side === "right") {
            this.addClass("sidebar_1-right");
        } else {
            this.addClass("sidebar_1-left");
        }

        oldCode = this.html();

        newCode += "<div class=\"row\">\n";
        newCode += "	<div class=\"col-xs-12 col-sm-12 col-md-12 col-lg1-12\" data-side=\"" + side + "\">\n" + oldCode + " </div>\n";
        newCode += "</div>";
        newCode += "<div class=\"toggler\">\n";
        newCode += "	<span class=\"glyphicon glyphicon-chevron-right\">&nbsp;</span> <span class=\"glyphicon glyphicon-chevron-left\">&nbsp;</span>\n";
        newCode += "</div>\n";

        this.html(newCode);

        if (autoClose) {
            $(this).find(".toggler").trigger("click");
        }

    };

    $(document).on('click', '.sidebar_1 .list-group-item', function () {
        $('.sidebar_1 .list-group-item').each(function () {
            $(this).removeClass('active');
        });
        $(this).addClass('active');
    });

    $(document).on('click', '.sidebar_1 .list-group-item', function (event) {
        var idToToggle, this_offset, this_x, this_y, href, side;
        event.preventDefault();
        href = $(this).attr('href');

        if (href.substr(0, 1) === '#') {

            idToToggle = href.substr(1, href.length);

            if (searchSubMenu(idToToggle)) {

                this_offset = $(this).offset();
                side = $(this).parent().parent().attr('data-side');

                var id = "#" + idToToggle;
                if (side === 'left') {
                    this_x = $(this).width() + 10;
                    this_y = this_offset.top + 1;
                    $(id).css('left', this_x);
                    $(id).css('top', this_y);
                } else if (side === 'right') {
                    this_x = $(this).width() + 10;
                    this_y = this_offset.top + 1;
                    $(id).css('right', this_x);
                    $(id).css('top', this_y);
                }

                $(id).fadeIn();

            } else {
                $('.submenu').fadeOut();
            }
        }
    });

    $(document).on('click', '.toggler', function () {
        var toggler = $(this);
        var container = toggler.parent();
        var listaClassi = container[0].classList;
        var side = getSide(listaClassi);
        var containerWidth = container.width();
        var status = container.attr('data-status');
        if (!status) {
            status = "opened";
        }
        doAnimation(container, containerWidth, side, status);
    });

    function searchSubMenu(id) {
        var found = false;
        $('.submenu').each(function () {
            var thisId = $(this).attr('id');
            if (id === thisId) {
                found = true;
            }
        });
        return found;
    }

    function getSide(listaClassi) {
        var side;
        for (var i = 0; i < listaClassi.length; i++) {
            if (listaClassi[i] === 'sidebar_1-left') {
                side = "left";
                break;
            } else if (listaClassi[i] === 'sidebar_1-right') {
                side = "right";
                break;
            } else {
                side = null;
            }
        }
        return side;
    }

    function doAnimation(container, containerWidth, sidebar_1Side, sidebar_1Status) {
        var toggler = container.children()[1];
        if (sidebar_1Status === "opened") {
            if (sidebar_1Side === "left") {
                container.animate({
                    left: -(containerWidth + 2)
                });
                toggleArrow(toggler, "left");
            } else if (sidebar_1Side === "right") {
                container.animate({
                    right: -(containerWidth + 2)
                });
                toggleArrow(toggler, "right");
            }
            container.attr('data-status', 'closed');
        } else {
            if (sidebar_1Side === "left") {
                container.animate({
                    left: 0
                });
                toggleArrow(toggler, "right");
            } else if (sidebar_1Side === "right") {
                container.animate({
                    right: 0
                });
                toggleArrow(toggler, "left");
            }
            container.attr('data-status', 'opened');
        }
    }

    function toggleArrow(toggler, side) {
        if (side === "left") {
            $(toggler).children(".glyphicon-chevron-right").css('display', 'block');
            $(toggler).children(".glyphicon-chevron-left").css('display', 'none');
        } else if (side === "right") {
            $(toggler).children(".glyphicon-chevron-left").css('display', 'block');
            $(toggler).children(".glyphicon-chevron-right").css('display', 'none');
        }
    }

}(jQuery));
