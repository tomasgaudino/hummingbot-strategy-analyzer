<body>
  <h1>Experimental Project</h1>
  <p>This project is still in its experimental phase, and while we are working hard to improve it, it may still contain bugs.

We believe this project has great potential, and we are committed to continuously improving it. If you'd like to help us on this journey, we'd love for you to collaborate with us! Whether you're a seasoned developer or just starting out, there's a place for you here.

Please feel free to open issues for bug reports or feature requests, and we'll do our best to address them as soon as possible. We welcome all contributions, from small bug fixes to major feature enhancements. Let's build something amazing together!</p>
  
  <h1> Run it with Docker!</h1>
  <p>Use the following command to run it with the available Dockerhub image:</p>
  
  <code>docker run -p 8501:8501 drupman08/hummingbot-strategy-analyzer</code>
  
  <h1>Guide to Using the Hummingbot Strategies Analyzer</h1>
  <p>This project is in development state. Please don't exconsists of two Streamlit pages:</p>
  <ol>
    <li>
      <p><strong>00_Query.py:</strong> creates a query based on a YAML configuration file, start and end date, and completes the analysis with private authentication credentials. The result is exported as an .xlsx file that can be loaded into the second page.</p>
    </li>
    <li>
      <p><strong>01_Dashboard.py:</strong> loads the .xlsx file from the previous page and creates a dashboard.</p>
    </li>
  </ol>
  <h2>Using 00_Query.py</h2>
  <p>Here are the steps for using 00_Query.py:</p>
  <ol>
    <li>
      <p><strong>Step 1: Choose your strategy</strong></p>
      <p>Choose your desired strategy from the available options and upload a strategy file if needed.</p>
    </li>
    <li>
      <p><strong>Step 2: Set parameters</strong></p>
      <p>Enter the start date and end date for the analysis.</p>
    </li>
    <li>
      <p><strong>Step 3: Authentication credentials</strong></p>
      <p>Upload the YAML file containing the authentication credentials for the analysis.</p>
    </li>
    <li>
      <p><strong>Step 4: Generate query</strong></p>
      <p>Click the "Generate query!" button to start the analysis.</p>
    </li>
    <li>
      <p><strong>Step 5: Download results</strong></p>
      <p>Download the .xlsx file containing the results of the analysis.</p>
    </li>
  </ol>
</body>
<h2> 01_Dashboard demo: screenshots from grid strategy trading </h2

![image](https://user-images.githubusercontent.com/69804854/216472569-cee7f9dc-e4ee-4aa4-98da-ec0833a732ba.png)
![image](https://user-images.githubusercontent.com/69804854/216472654-6731f89b-ece0-401a-ba31-520d1018d870.png)
