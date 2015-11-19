/**
 * Created by valerio on 06/02/14.
 */

(function($){

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function set_agreement_vote(select) {
        var evaluation_id = select.attr('name');
        $.ajax({
            url: "./" + evaluation_id + "/agreement/",
            data: "evaluation=" + select.find(":selected").val(),
            type: "POST",
            complete: function (xmlHttpRequest, message) {
                if (message == 'success') {
                    if (select.find(":selected").val() == '-1'){
                        select.parent().parent().attr("style", "border: 2px solid #ddd !important");
                    } else {
                        select.parent().parent().attr("style", "border: 2px solid green !important");
                    }
                } else {
                    select.parent().parent().attr("style", "border: 2px solid red !important");
                }
            }
        });
    }

    function set_wrong_association(checkbox) {
        var evaluation_id = checkbox.attr('name').split('-')[1];
        var data = 0;
        if (checkbox.is(':checked')) {
            data = 1;
        }
        $.ajax({
            url: "./" + evaluation_id + "/wrong-association/",
            data: "wrong=" + data,
            type: "POST",
            complete: function (xmlHttpRequest, message) {
                if (message == 'success') {
                    toggle_select_state(evaluation_id, checkbox);
                    checkbox.parent().parent().attr("style", "border: 2px solid #ddd !important");
                }
            }
        });
    }

    function toggle_select_state(evaluation_id, checkbox) {
        var select = $('#id_agreement_vote-' + evaluation_id);
        if (checkbox.is(':checked')) {
            select.val('-1');
            select.prop('disabled', true);
        } else {
            select.prop('disabled', false);
        }
    }

    $(document).ready(function(){

        $("input[name^='wrong_association-']").each(function(){
            var evaluation_id = $(this).attr('name').split('-')[1];
            toggle_select_state(evaluation_id, $(this));

            $(this).change(function(){
                set_wrong_association($(this));
            });

        });

        $("select[id^='id_agreement_vote-']").change(function(){
            set_agreement_vote($(this));
        });


        // Change Form Activations
        $("#id_wrong_association").each(function(){
            toggle_select_state('', $(this));

            $(this).change(function(){
                toggle_select_state('', $(this));
            });

        });

    })
})(django.jQuery);
