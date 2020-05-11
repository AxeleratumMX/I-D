
<template>
    <div class="col-sm-12">
		<div :style="{'height': table_height}">
			<table id="establishment_table" ref="establishment_table"
				class="table col-sm-12 offset-sm-0 col-md-8 offset-md-2">
				<thead>
					<tr>
						<th v-for="column in columns"><div v-if="!column.hide || column.hide == false">{{ column.name }}</div></th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="row in rows">
						<td v-for="column in columns">
							<div v-if="column.is_html">
								<div v-html="row[column.key]"></div>
							</div>
							<div v-else>
								<div v-html="row[column.key]"></div>
							</div>
						</td>
						<!-- td><button type="button" class="btn btn-light" style="padding: 0;"
							data-toggle="modal" data-target="#establishment_info"><span
								class="material-icons">info</span></button></td -->
					</tr>
				</tbody>
			</table>
		</div>

		<div class="d-flex justify-content-center mt-5">
			<nav aria-label="Page navigation example">
  				<ul class="pagination pagination-sm">
					<li class="page-item"><a class="page-link" v-on:click="change_page(1)">&laquo;</a></li>
					<li class="page-item"><a class="page-link" v-on:click="change_page(current_page - 1)"><</a></li>
					<li v-for="page in pages_range" v-bind:class="{'page-item':true, 'active': (page + start_page - 1 == current_page)}">
						<a class="page-link" v-on:click="change_page(page + start_page - 1)">{{ page + start_page - 1}}</a>
					</li>
					<li class="page-item"><a class="page-link" v-on:click="change_page(current_page + 1)">></a></li>
					<li class="page-item"><a class="page-link" v-on:click="change_page(total_pages)">&raquo;</a></li>
  				</ul>
			</nav>
    	</div>
	</div>
</template>


<script>
export default {
  	name: 'datatable',
  	props: ['columns', 'data-key', 'pages-range', 'current-page-key', 'total-pages-key', 'table-height'],
	methods: {
        change_page(page) {
			if(page < 1){
				page = 1;
			}

			if(page > this.$store.state[this.$props.totalPagesKey]){
				page = this.$store.state[this.$props.totalPagesKey];
			}

            this.$store.dispatch('load_page', {page: page}).then(() => {
				// Display spinner
			});
			
			this.$store.dispatch('update_current_page', {page: page});
        }
    },
	computed: {
		rows() {
			return this.$store.state[this.$props.dataKey];
		},
		current_page() {
			return this.$store.state[this.$props.currentPageKey];
		},
		start_page(){

			var pages_range = this.$props.pagesRange;

			if(this.$store.state[this.$props.totalPagesKey] > pages_range *  2 + 1){
				var start_page = this.$store.state[this.$props.currentPageKey] - pages_range;
				var end_page = start_page + pages_range * 2 + 1;

				if(start_page <= 0){
					start_page = 1;
				}
				
				if(end_page > this.$store.state[this.$props.totalPagesKey]){
					start_page = this.$store.state[this.$props.totalPagesKey] - pages_range * 2;
				}

			}
			else{
				start_page = 1;
			}


			return start_page;
		},
		pages_range(){
			var range = this.$props.pagesRange * 2 + 1;
			
			if( range > this.$store.state[this.$props.totalPagesKey] ){
				range = this.$store.state[this.$props.totalPagesKey];
			}

			return range;
		},
		total_pages(){
			return this.$store.state[this.$props.totalPagesKey];
		},
		table_height() {
			return this.$props.tableHeight + 'px';			
		}
	}
}
</script>

<style lang="scss">
</style>
