function get_current_file_id() {
    var selectedElements = document.getElementsByClassName('selected');
    var element = selectedElements[0];
    //console.log(element.id);
    return element.id;
}
function get_file_path_list(elementId, currentPath) {
    var element = document.getElementById(elementId);
    var current_name = element.childNodes[0].innerHTML;
    if (element.classList.contains('is-dir')) {
        currentPath.push(current_name);
    }
    if (element.parentNode.parentNode.nodeName === 'UL') {
        var liElement = element.parentNode.parentNode.parentNode;
        if (liElement.nodeName === 'LI') {
            get_file_path_list(liElement.childNodes[0].id, currentPath);
        }
    }
    return currentPath;
}

function get_file_path() {
    var path_list = get_file_path_list(get_current_file_id(), []);
    //path_list = path_list.reverse();
    var path = path_list.reverse().join("/");
    if (path === "/") {

    } else {
        path = path.substring(1);
    }
    //path.append('/');
    return path;
}
function get_full_file_path_list(elementId, currentPath) {
    var element = document.getElementById(elementId);
    var current_name = element.childNodes[0].innerHTML;
    currentPath.push(current_name);
    if (element.parentNode.parentNode.nodeName === 'UL') {
        var liElement = element.parentNode.parentNode.parentNode;
        if (liElement.nodeName === 'LI') {
            get_file_path_list(liElement.childNodes[0].id, currentPath);
        }
    }
    return currentPath;
}

function get_full_file_path() {
    var path_list = get_full_file_path_list(get_current_file_id(), []);
    //path_list = path_list.reverse();
    var path = path_list.reverse().join("/");
    if (path === "/") {

    } else {
        path = path.substring(1);
    }
    //path.append('/');
    return path;
}
function check_is_dir() {
    var elementId = get_current_file_id();
    var element = document.getElementById(elementId);
    if (element.classList.contains('is-dir')) {
        return true;
    } else {
        return false;
    }
}

const json_name = "/static/test.json"
var id = 1;
var path = "";
var full_path = "";
function generate_list(data, parentElement) {

    if (!Array.isArray(data)) {
        data = [data];
    }

    $.each(data, function (index, item) {
        var li = $('<li></li>');
        var div = $('<div></div>').addClass('selectable-block');
        var span = $('<span></span>').text(item.name);
        div.append(span);
        li.append(div);

        div.attr('id', 'element' + id);
        id++;

        if (item.isdir) {
            div.addClass('is-dir');
            var children = $('<ul></ul>').addClass('sublist');
            generate_list(item.children, children);
            li.append(children);
        } else {
            div.addClass('is-file');
        }

        parentElement.append(li);
    });

    parentElement.find('.selectable-block').click(function () {
        $('.selectable-block').removeClass('selected');
        $(this).addClass('selected');
        //get_current_file_id();
        path = get_file_path(get_current_file_id(), []);
        document.getElementById("path_value").value = path;
        full_path = get_full_file_path(get_current_file_id(), []);
        document.getElementById("full_path_value").value = full_path;
        document.getElementById("download_is_dir").value = check_is_dir();
        document.getElementById("remove_is_dir").value = check_is_dir();
        document.getElementById("dir_path_value").value = path;
        document.getElementById("download_path_value").value = full_path;
        document.getElementById("download_id").value = get_current_file_id();
        console.log(path);
    });
}