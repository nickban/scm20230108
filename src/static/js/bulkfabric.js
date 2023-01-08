
$(function () {
  // 大货布进度弹出页面
    $('.js-create-bf').click(function () {
      var parent = $(this).parent()
      var ul = parent.find('.list-unstyled')
      var id = ul.attr("id");
      var idno = id.slice(2)
      url = '/order/' + idno + '/progress/bf/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
          $("#modal-bf").modal("show");
        },
        success: function (data) {
          $("#modal-bf .modal-content").html(data.html_form);
        }
      });
    });
    // 大货布进度页面保存
    $("#modal-bf").on("submit", ".js-bf-create-form", function () {
      var form = $(this);
      $.ajax({
        url: form.attr("action"),
        data: form.serialize(),
        type: form.attr("method"),
        dataType: 'json',
        success: function (data) {
          // 订单的pk
          pk = data['pk']
          // 找到ul的id
          id = 'bf' + pk
          //找到ul
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_bf_list);
            $("#modal-bf").modal("hide");
          }
          else {
            $("#modal-bf .modal-content").html(data.html_form);
          }
        }
      });
      // 一定要用结束改程序执行的语句结尾, 否则数据出错
      return false;
    });
    // 大货布进度删除,由于是动态生产的，一定要下面的这种写法
    $(document).on('click', '.bf-delete', function () {
      // 获得bf的id
      var id = $(this).attr("id");
      var idno = id.slice(3)
      url = '/order/' + 'bf/' + idno + '/delete/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (data) {
          pk = data['pk']
          id = 'bf' + pk
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_bf_list);
            $("#modal-bf").modal("hide");
          }
        }
      });
    });
    // 大货布进度编辑,注意动态内容的写法
    $(document).on('click', '.bf-edit', function () {
      var id = $(this).attr("id");
      var idno = id.slice(3)
      url = '/order/' + 'bf/' + idno + '/edit/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
          $("#modal-bf").modal("show");
        },
        success: function (data) {
          pk = data['pk']
          id = 'bf' + pk
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_bf_list);
            $("#modal-bf").modal("hide");
          }
          else {
            $("#modal-bf .modal-content").html(data.html_form);
          }
        }
      });
    });
  });
