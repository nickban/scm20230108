
$(function () {
    // 显示全部qcreport记录
    $('.js-list-qrall').click(function () {
      var parent = $(this).parent()
      var ul = parent.find('.list-unstyled')
      var id = ul.attr("id");
      var idno = id.slice(2)
      url = '/order/' + idno + '/qcreports/all/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (data) {
          pk = data['pk']
          id = 'qr' + pk
          element = $('#' + id);
          element.html(data.html_qr_list);
        }
      });
    });
    // 显示3条qcreport记录
    $('.js-list-qr3').click(function () {
      var parent = $(this).parent()
      var ul = parent.find('.list-unstyled')
      var id = ul.attr("id");
      var idno = id.slice(2)
      url = '/order/' + idno + '/qcreports/3/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (data) {
          pk = data['pk']
          id = 'qr' + pk
          element = $('#' + id);
          qs_showlist = data['qs_showlist']
          element.html(data.html_qr_list);
          }
        });
      });
    });

