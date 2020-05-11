import Vue from 'vue';
import Navbar from './components/Navbar.vue'
import Datatable from './components/Datatable.vue';
import Vuex from 'vuex';

Vue.use(Vuex);


new Vue({
    el:'#navbar',
    components: {
        'navbar': Navbar
    },
    data: function() {
        return {
          active_item: "files",
        }
    }
})






var store = new Vuex.Store({
    state: {
        current_page: 1,
        files: [],
        total_pages: 1
    },
    mutations: {
        update_data(state, files) {
            state.files = files;
        },
        update_page(state, page) {
            state.current_page = page;
        },
        update_total_pages(state, total_pages){
            state.total_pages = total_pages;
        }
    },
    actions: {
        load_page(context, params) {
            return new Promise((resolve) => {
                /*this.$http.get('...').then((response) => {
                    context.commit('updateMessage', response.data.message);
                    resolve();
                });*/

                if(params.page <= 0){
                    params.page = 1;
                }

                context.commit(
                    'update_data', 
                    [{ name: 'Nombre ' + (params.page * 1), creation_date: '2019-03-01', information: '<button type="button" class="btn btn-light" style="padding: 0;" data-toggle="modal" data-target="#establishment_info"><span class="material-icons">info</span></button>' }, 
                    { name: 'Nombre ' + (params.page * 2), creation_date: '2019-03-01' }]
                    
                );

                context.commit('update_total_pages', 1000000);

                resolve();
                
            });
        },

        update_current_page(context, params) {
            context.commit('update_page', params.page);
        }
    }

});


var files_table = new Vue({
    el: '#files_table',
    store: store,
    components: {
        'datatable': Datatable
    },
    data: function () {
        return {
            columns: [
                {
                    name: 'Nombre', 
                    key: 'name'
                }, {
                    name: 'Fecha de alta', 
                    key: 'creation_date'
                }, {
                    hide: true, 
                    name: 'Información', 
                    key: 'information',
                    is_html: true
                }
            ],
            data_key: 'files',
            current_page_key: 'current_page',
            total_pages_key: 'total_pages'
        }
    }
});


files_table.$on('change-page', function (page) {
    this.$refs.files_datatable.change_page(page);
});

files_table.$emit('change-page', 0);