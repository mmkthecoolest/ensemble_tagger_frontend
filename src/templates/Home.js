const Home = () => {
	return (<div>
		<title>Ensemble Tagger</title>
		<h1>Choose Upload Type</h1>
		<form action="upload_file">
			<input type="submit" value="Upload a File" />
		</form>
		<form action="upload_folder_srcml">
			<input type="submit" value="Upload a Folder" />
		</form>
	</div>)
}

export default Home;