<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
		<a class="navbar-brand ml-1" href="panel.html">
			<img class="" src="/dist/img/h_lg_light_logo.png" alt="" width="72" height="30" />
		</a>

		<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar_content"
			aria-controls="navbar_content" aria-expanded="false" aria-label="Toggle navigation">
			<span class="navbar-toggler-icon"></span>
		</button>

		<div class="collapse navbar-collapse" id="navbar_content">
			<ul class="navbar-nav ml-auto mr-1">

				{{active_item.lowerCase}}
				<li v-bind:class="{'nav-item':true, 'active':(active_item.toLowerCase() == 'panel')}">
					<a class="nav-link" href="panel.html">Panel</a>
				</li>

				<li v-bind:class="{'nav-item':true, 'active':(active_item.toLowerCase() == 'files')}">
					<a class="nav-link" href="files.html">Archivos</a>
				</li>	



				<li class="nav-item dropdown ml-3">
					<a class="nav-link dropdown-toggle" href="#" id="user_menu" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
						<img class="rounded-circle" src="/dist/img/default_avatar.jpg" alt="" width="30" height="30" />
					</a>
					<div class="dropdown-menu dropdown-menu-right" aria-labelledby="user_menu">
						<a class="dropdown-item" href="user_information.html">Mi información</a>
						<div class="dropdown-divider"></div>
						<a class="dropdown-item" href="#">Cerrar sesión</a>
					</div>
				</li>			
			</ul>
		</div>
	</nav>  
</template>


<script>
export default {
  name: 'navbar',
  props: ['active_item']
}
</script>

<style lang="scss">
</style>
