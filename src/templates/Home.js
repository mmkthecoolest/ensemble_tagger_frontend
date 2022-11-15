const Home = () => {
	return (<div className="menu-page">
		<title>Ensemble Tagger</title>
		<h1>Choose Upload Type</h1>
		<div className="home-buttons-flexbox">
		<form action="upload_file">
			<input type="submit" value="Upload a File" className="custom-button"/>
		</form>
		<form action="upload_folder">
			<input type="submit" value="Upload a Folder" className="custom-button"/>
		</form>
		</div>
	</div>)
}

export default Home;