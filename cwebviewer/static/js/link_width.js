    $(document).ready(function() {
        width = $(window).width();
        height = $(window).height();
        // console.log('width ' + width + ' height ' + height);
        $('a.imglink').each(function(o) {
            $(this).attr("href", $(this).attr("href") + '?width=' + Math.max(width, height));
        });
    });
