/*
SelectFilter2 - Turns a multiple-select box into a filter interface.

Different than SelectFilter because this is coupled to the admin framework.

Requires core.js, SelectBox.js and addevent.js.
*/

function findForm(node) {
    // returns the node of the form containing the given node
    if (node.tagName.toLowerCase() != 'form') {
        return findForm(node.parentNode);
    }
    return node;
}

var SelectFilter = {
    init: function(field_id, field_name, is_stacked, admin_media_prefix) {
        if (field_id.match(/__prefix__/)){
            // Don't intialize on empty forms.
            return;
        }
        var from_box = document.getElementById(field_id);
        from_box.id += '_from'; // change its ID
        from_box.className = 'filtered';

        var ps = from_box.parentNode.getElementsByTagName('p');
        for (var i=0; i<ps.length; i++) {
            if (ps[i].className.indexOf("info") != -1) {
                // Remove <p class="info">, because it just gets in the way.
                from_box.parentNode.removeChild(ps[i]);
            } else if (ps[i].className.indexOf("help") != -1) {
                // Move help text up to the top so it isn't below the select
                // boxes or wrapped off on the side to the right of the add
                // button:
                from_box.parentNode.insertBefore(ps[i], from_box.parentNode.firstChild);
            }
        }

        // <div class="selector"> or <div class="selector stacked">
        var selector_div = quickElement('div', from_box.parentNode);
        selector_div.className = is_stacked ? 'selector stacked' : 'selector';

        // <div class="selector-available">
        var selector_available = quickElement('div', selector_div, '');
        selector_available.className = 'selector-available';
        quickElement('h2', selector_available, interpolate(gettext('Available %s'), [field_name]));
        var filter_p = quickElement('p', selector_available, '');
        filter_p.className = 'selector-filter';

        var search_filter_label = quickElement('label', filter_p, '', 'for', field_id + "_input", 'style', 'width:16px;padding:2px');

        var search_selector_img = quickElement('img', search_filter_label, '', 'src', 'data:image/gif;base64,R0lGODlhEAAQAOYAAND/2jw8PP39/UlJSfLy8kBAQEtLS0xMTDo6OmVlZTg4OD4+Pt3d3WpqajY2NsvLy9PT06urq1hYWEdHR2BgYNbW1kNDQ0VFRZSUlH19fZ2dnYODg2NjY1tbW2xsbF9fX/X19Z6enuzs7OTk5Lm5ueXl5VNTU9TU1KqqqsHBwdHR0U5OTunp6WZmZsXFxZqamlVVVXt7e9DQ0FpaWn5+fpmZmT8/P4aGhpubm3x8fM/Pz+Dg4GlpaZOTk15eXoiIiNjY2OHh4YKCgmRkZNvb29/f30FBQQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAAALAAAAAAQABAAAAeFgACCg4SFhCEdFxYHG4aDNAMTLQkDBT6OGgYUDwQEFTwLGYYfBg8CpwIMKwGGBw0EpyAsQTGsha4iJRA6EBU/toQwJi4qJ0BERTPAg0IGOTIMOyM3C0OOlBI9GBQFCxyOAB4TikYJEgEIEeCEJOgK6uuCOAgKDijxgjX1BfiCLzYp+hUKBAA7');
        search_selector_img.alt = gettext("Filter");

        filter_p.appendChild(document.createTextNode(' '));

        var filter_input = quickElement('input', filter_p, '', 'type', 'text');
        filter_input.id = field_id + '_input';
        selector_available.appendChild(from_box);
        var choose_all = quickElement('a', selector_available, gettext('Choose all'), 'href', 'javascript: (function(){ SelectBox.move_all("' + field_id + '_from", "' + field_id + '_to"); })()');
        choose_all.className = 'selector-chooseall';

        // <ul class="selector-chooser">
        var selector_chooser = quickElement('ul', selector_div, '');
        selector_chooser.className = 'selector-chooser';
        var add_link = quickElement('a', quickElement('li', selector_chooser, ''), gettext('Add'), 'href', 'javascript: (function(){ SelectBox.move("' + field_id + '_from","' + field_id + '_to");})()');
        add_link.className = 'selector-add';
        var remove_link = quickElement('a', quickElement('li', selector_chooser, ''), gettext('Remove'), 'href', 'javascript: (function(){ SelectBox.move("' + field_id + '_to","' + field_id + '_from");})()');
        remove_link.className = 'selector-remove';

        // <div class="selector-chosen">
        var selector_chosen = quickElement('div', selector_div, '');
        selector_chosen.className = 'selector-chosen';
        quickElement('h2', selector_chosen, interpolate(gettext('Chosen %s'), [field_name]));
        var selector_filter = quickElement('p', selector_chosen, gettext('Select your choice(s) and click '));
        selector_filter.className = 'selector-filter';
        quickElement('img', selector_filter, '', 'src', (is_stacked ? 'data:image/gif;base64,R0lGODlhEAAQAOZVAIapzdrk76O914msz4Woy+Lq83ugxn6ix7TJ3+7z+ICkyYOmyarC2pOy0unv9rXL4vH1+Y6tzurw9+Dp8pq51+/0+P3+/uvx94iqzbPI3rjP5pCx0rLJ4ZWz1ICkyp661pa11KK+27TM5LbN5Y+v0Jm31Yqszp251n+jyZi41nyhxrTK4LTJ4Ovw9oCjyJm414Ony4Kmynyhx6S/2+zy94+w0afB25Gx0n6jyKXB3H+kyYepzLbK346u0Nrl8LnN4qO+2pKx04Klyn2hx3+jyISozLLK432ix7zQ5IeqzbHH3aXA3LPL45262I6v0Za01ZOz05e21azG4I+v0fX4+////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAFUALAAAAAAQABAAAAfBgFWCVRMMCygeLgIBg4MWGQQhIhoaIzkYShWNSg1GTJ+gTCUqCYIIJFKpqqsgSlU0CjNLsxwPDxyzswQBPD1Nv00XVFQXwE0NAhFBT8xPEsMSzU8dBgdT19cOww7Y10MHA+EFBRDDEAU+GxsDMhFFAAAsw/NUJ/AABggxSfwr9B/8ksAQ0OKIk4NOfgwDgtCJDkYICECZCAWJDYpQMA1SsiOKx48eTRgoJeiRghopKFB4cUNIpkaCCi3AQeTAokaBAAA7':'data:image/gif;base64,R0lGODlhEAAQAOZZAIapzYmsz4+v0drk7+fu9Za01aO913ugxoWoy36ix7TJ3+rw9+Dp8rjP5oOmyZq514Ckyf3+/u7z+LPI3oiqzY6tzpOy0u/0+KrC2n+jyb7Q5YOny5m31YCjyI+v0H2ix+Hq85a11LnN4qO92aO+2p251nyhx4Klypm416W/27bN5J661n+kybLK4/P2+oKmyn2hx5q41vH1+bbK336jyJGx0o6u0Ovw9rbN5aS/24SozMLU59zm8Yqszpi41nyhxo+w0YCkype11IepzOzy95+82Onv9qK+256717TM5JWz1MfY6aXB3JKx03+jyLHH3bPL45e21Z262KzG4JOz04eqzaXA3I6v0fX4+////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAFkALAAAAAAQABAAAAe7gFmCWQwYDhlBHQYDg4MREwhHSQ0NOEwUTxeNTxYtUJ+gUBw/EoIKHlOpqSqqUyFPWUQQOVa1tUZLtlYIAzM2UsDBBFg7wRYGFU0FBSkLzi5YWBrLSgcJAtgj0dvRItgwCQHiSNzbReImFToAAEIE7zLRJewABwovVfn6IFgr+hsGbny4QrAgDxIFr7BgpAABlYcPY0CkgmnQkyFRMmrM2ONAKUGPIADx8eABihonMjUSVMgBDScJFjUKBAA7'), 'alt', 'Add');
        var to_box = quickElement('select', selector_chosen, '', 'id', field_id + '_to', 'multiple', 'multiple', 'size', from_box.size, 'name', from_box.getAttribute('name'));
        to_box.className = 'filtered';
        var clear_all = quickElement('a', selector_chosen, gettext('Clear all'), 'href', 'javascript: (function() { SelectBox.move_all("' + field_id + '_to", "' + field_id + '_from");})()');
        clear_all.className = 'selector-clearall';

        from_box.setAttribute('name', from_box.getAttribute('name') + '_old');

        // Set up the JavaScript event handlers for the select box filter interface
        addEvent(filter_input, 'keyup', function(e) { SelectFilter.filter_key_up(e, field_id); });
        addEvent(filter_input, 'keydown', function(e) { SelectFilter.filter_key_down(e, field_id); });
        addEvent(from_box, 'dblclick', function() { SelectBox.move(field_id + '_from', field_id + '_to'); });
        addEvent(to_box, 'dblclick', function() { SelectBox.move(field_id + '_to', field_id + '_from'); });
        addEvent(findForm(from_box), 'submit', function() { SelectBox.select_all(field_id + '_to'); });
        SelectBox.init(field_id + '_from');
        SelectBox.init(field_id + '_to');
        // Move selected from_box options to to_box
        SelectBox.move(field_id + '_from', field_id + '_to');
    },
    filter_key_up: function(event, field_id) {
        from = document.getElementById(field_id + '_from');
        // don't submit form if user pressed Enter
        if ((event.which && event.which == 13) || (event.keyCode && event.keyCode == 13)) {
            from.selectedIndex = 0;
            SelectBox.move(field_id + '_from', field_id + '_to');
            from.selectedIndex = 0;
            return false;
        }
        var temp = from.selectedIndex;
        SelectBox.filter(field_id + '_from', document.getElementById(field_id + '_input').value);
        from.selectedIndex = temp;
        return true;
    },
    filter_key_down: function(event, field_id) {
        from = document.getElementById(field_id + '_from');
        // right arrow -- move across
        if ((event.which && event.which == 39) || (event.keyCode && event.keyCode == 39)) {
            var old_index = from.selectedIndex;
            SelectBox.move(field_id + '_from', field_id + '_to');
            from.selectedIndex = (old_index == from.length) ? from.length - 1 : old_index;
            return false;
        }
        // down arrow -- wrap around
        if ((event.which && event.which == 40) || (event.keyCode && event.keyCode == 40)) {
            from.selectedIndex = (from.length == from.selectedIndex + 1) ? 0 : from.selectedIndex + 1;
        }
        // up arrow -- wrap around
        if ((event.which && event.which == 38) || (event.keyCode && event.keyCode == 38)) {
            from.selectedIndex = (from.selectedIndex == 0) ? from.length - 1 : from.selectedIndex - 1;
        }
        return true;
    }
}
