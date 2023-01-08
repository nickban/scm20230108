
$(function () {
    // 显示全部fs记录
    $('.js-list-fsall').click(function () {
      var parent = $(this).parent()
      var ul = parent.find('.list-unstyled')
      var id = ul.attr("id");
      var idno = id.slice(2)
      url = '/order/' + idno + '/progress/fs/all/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (data) {
          pk = data['pk']
          id = 'fs' + pk
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_fs_list);
          }
        }
      });
    });
        // 显示3条fs记录
        $('.js-list-fs3').click(function () {
          var parent = $(this).parent()
          var ul = parent.find('.list-unstyled')
          var id = ul.attr("id");
          var idno = id.slice(2)
          url = '/order/' + idno + '/progress/fs/3/'
          $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            success: function (data) {
              pk = data['pk']
              id = 'fs' + pk
              element = $('#' + id);
              if (data.form_is_valid) {
                element.html(data.html_fs_list);
              }
            }
          });
        });
  // 生产板进度弹出页面
    $('.js-create-fs').click(function () {
      var parent = $(this).parent()
      var ul = parent.find('.list-unstyled')
      var id = ul.attr("id");
      var idno = id.slice(2)
      url = '/order/' + idno + '/progress/fs/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
          $("#modal-fs").modal("show");
        },
        success: function (data) {
          $("#modal-fs .modal-content").html(data.html_form);
        }
      });
    });
    // 生产板进度页面保存
    $("#modal-fs").on("submit", ".js-fs-create-form", function () {
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
          id = 'fs' + pk
          //找到ul
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_fs_list);
            $("#modal-fs").modal("hide");
          }
          else {
            $("#modal-fs .modal-content").html(data.html_form);
          }
        }
      });
      // 一定要用结束改程序执行的语句结尾, 否则数据出错
      return false;
    });
    // 生产板进度删除,由于是动态生产的，一定要下面的这种写法
    $(document).on('click', '.fs-delete', function () {
      // 获得fs的id
      var id = $(this).attr("id");
      var idno = id.slice(3)
      url = '/order/' + 'fs/' + idno + '/delete/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (data) {
          pk = data['pk']
          id = 'fs' + pk
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_fs_list);
            $("#modal-fs").modal("hide");
          }
        }
      });
    });
    // 生产板进度编辑,注意动态内容的写法
    $(document).on('click', '.fs-edit', function () {
      var id = $(this).attr("id");
      var idno = id.slice(3)
      url = '/order/' + 'fs/' + idno + '/edit/'
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
          $("#modal-fs").modal("show");
        },
        success: function (data) {
          pk = data['pk']
          id = 'fs' + pk
          element = $('#' + id);
          if (data.form_is_valid) {
            element.html(data.html_fs_list);
            $("#modal-fs").modal("hide");
          }
          else {
            $("#modal-fs .modal-content").html(data.html_form);
          }
        }
      });
    });
  });
