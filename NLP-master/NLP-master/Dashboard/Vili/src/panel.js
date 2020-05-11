import Vue from 'vue';
import Navbar from './components/Navbar.vue'
import 'jquery'

new Vue({
    el:'#navbar',
    components: {
        'navbar': Navbar
    },
    data: function() {
        return {
          active_item: "panel",
        }
    }
})
