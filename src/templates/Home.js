const Home = () => {
	return (<div>
		<title>Ensemble Tagger</title>
		<h1>Choose Upload Type</h1>
		<form action="upload_file_srcml">
			<input type="submit" value="Use srcML on File" />
		</form>
		<form action="upload_file_annotate">
			<input type="submit" value="Annotate a file" />
		</form>
		<form action="upload_folder_srcml">
			<input type="submit" value="Use srcML on Folder" />
		</form>
	</div>)
}

export default Home;