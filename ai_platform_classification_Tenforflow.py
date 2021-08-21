#!/usr/bin/env python
# coding: utf-8

# ## AI Platform: Qwik Start
# 
# This lab gives you an introductory, end-to-end experience of training and prediction on AI Platform. The lab will use a census dataset to:
# 
# - Create a TensorFlow 2.x training application and validate it locally.
# - Run your training job on a single worker instance in the cloud.
# - Deploy a model to support prediction.
# - Request an online prediction and see the response.

# In[1]:


import os


# ### Step 1: Get your training data
# 
# The relevant data files, adult.data and adult.test, are hosted in a public Cloud Storage bucket.
# 
# You can read the files directly from Cloud Storage or copy them to your local environment. For this lab you will download the samples for local training, and later upload them to your own Cloud Storage bucket for cloud training.
# 
# Run the following command to download the data to a local file directory and set variables that point to the downloaded data files:

# In[2]:


get_ipython().run_cell_magic('bash', '', '\nmkdir data\ngsutil -m cp gs://cloud-samples-data/ml-engine/census/data/* data/')


# In[3]:


get_ipython().run_cell_magic('bash', '', '\nexport TRAIN_DATA=$(pwd)/data/adult.data.csv\nexport EVAL_DATA=$(pwd)/data/adult.test.csv')


# Inspect what the data looks like by looking at the first couple of rows:

# In[4]:


get_ipython().run_cell_magic('bash', '', '\nhead data/adult.data.csv')


# ### Step 2: Run a local training job
# 
# A local training job loads your Python training program and starts a training process in an environment that's similar to that of a live Cloud AI Platform cloud training job.
# 

# #### Step 2.1: Create files to hold the Python program
# 
# To do that, let's create three files. The first, called util.py, will contain utility methods for cleaning and preprocessing the data, as well as performing any feature engineering needed by transforming and normalizing the data.

# In[5]:


get_ipython().run_cell_magic('bash', '', 'mkdir -p trainer\ntouch trainer/__init__.py')


# In[6]:


get_ipython().run_cell_magic('writefile', 'trainer/util.py', 'from __future__ import absolute_import\nfrom __future__ import division\nfrom __future__ import print_function\n\nimport os\nfrom six.moves import urllib\nimport tempfile\n\nimport numpy as np\nimport pandas as pd\nimport tensorflow as tf\n\n# Storage directory\nDATA_DIR = os.path.join(tempfile.gettempdir(), \'census_data\')\n\n# Download options.\nDATA_URL = (\n    \'https://storage.googleapis.com/cloud-samples-data/ai-platform/census\'\n    \'/data\')\nTRAINING_FILE = \'adult.data.csv\'\nEVAL_FILE = \'adult.test.csv\'\nTRAINING_URL = \'%s/%s\' % (DATA_URL, TRAINING_FILE)\nEVAL_URL = \'%s/%s\' % (DATA_URL, EVAL_FILE)\n\n# These are the features in the dataset.\n# Dataset information: https://archive.ics.uci.edu/ml/datasets/census+income\n_CSV_COLUMNS = [\n    \'age\', \'workclass\', \'fnlwgt\', \'education\', \'education_num\',\n    \'marital_status\', \'occupation\', \'relationship\', \'race\', \'gender\',\n    \'capital_gain\', \'capital_loss\', \'hours_per_week\', \'native_country\',\n    \'income_bracket\'\n]\n\n# This is the label (target) we want to predict.\n_LABEL_COLUMN = \'income_bracket\'\n\n# These are columns we will not use as features for training. There are many\n# reasons not to use certain attributes of data for training. Perhaps their\n# values are noisy or inconsistent, or perhaps they encode bias that we do not\n# want our model to learn. For a deep dive into the features of this Census\n# dataset and the challenges they pose, see the Introduction to ML Fairness\n# Notebook: https://colab.research.google.com/github/google/eng-edu/blob\n# /master/ml/cc/exercises/intro_to_fairness.ipynb\nUNUSED_COLUMNS = [\'fnlwgt\', \'education\', \'gender\']\n\n_CATEGORICAL_TYPES = {\n    \'workclass\': pd.api.types.CategoricalDtype(categories=[\n        \'Federal-gov\', \'Local-gov\', \'Never-worked\', \'Private\', \'Self-emp-inc\',\n        \'Self-emp-not-inc\', \'State-gov\', \'Without-pay\'\n    ]),\n    \'marital_status\': pd.api.types.CategoricalDtype(categories=[\n        \'Divorced\', \'Married-AF-spouse\', \'Married-civ-spouse\',\n        \'Married-spouse-absent\', \'Never-married\', \'Separated\', \'Widowed\'\n    ]),\n    \'occupation\': pd.api.types.CategoricalDtype([\n        \'Adm-clerical\', \'Armed-Forces\', \'Craft-repair\', \'Exec-managerial\',\n        \'Farming-fishing\', \'Handlers-cleaners\', \'Machine-op-inspct\',\n        \'Other-service\', \'Priv-house-serv\', \'Prof-specialty\', \'Protective-serv\',\n        \'Sales\', \'Tech-support\', \'Transport-moving\'\n    ]),\n    \'relationship\': pd.api.types.CategoricalDtype(categories=[\n        \'Husband\', \'Not-in-family\', \'Other-relative\', \'Own-child\', \'Unmarried\',\n        \'Wife\'\n    ]),\n    \'race\': pd.api.types.CategoricalDtype(categories=[\n        \'Amer-Indian-Eskimo\', \'Asian-Pac-Islander\', \'Black\', \'Other\', \'White\'\n    ]),\n    \'native_country\': pd.api.types.CategoricalDtype(categories=[\n        \'Cambodia\', \'Canada\', \'China\', \'Columbia\', \'Cuba\', \'Dominican-Republic\',\n        \'Ecuador\', \'El-Salvador\', \'England\', \'France\', \'Germany\', \'Greece\',\n        \'Guatemala\', \'Haiti\', \'Holand-Netherlands\', \'Honduras\', \'Hong\',\n        \'Hungary\',\n        \'India\', \'Iran\', \'Ireland\', \'Italy\', \'Jamaica\', \'Japan\', \'Laos\',\n        \'Mexico\',\n        \'Nicaragua\', \'Outlying-US(Guam-USVI-etc)\', \'Peru\', \'Philippines\',\n        \'Poland\',\n        \'Portugal\', \'Puerto-Rico\', \'Scotland\', \'South\', \'Taiwan\', \'Thailand\',\n        \'Trinadad&Tobago\', \'United-States\', \'Vietnam\', \'Yugoslavia\'\n    ]),\n    \'income_bracket\': pd.api.types.CategoricalDtype(categories=[\n        \'<=50K\', \'>50K\'\n    ])\n}\n\n\ndef _download_and_clean_file(filename, url):\n    """Downloads data from url, and makes changes to match the CSV format.\n\n    The CSVs may use spaces after the comma delimters (non-standard) or include\n    rows which do not represent well-formed examples. This function strips out\n    some of these problems.\n\n    Args:\n      filename: filename to save url to\n      url: URL of resource to download\n    """\n    temp_file, _ = urllib.request.urlretrieve(url)\n    with tf.io.gfile.GFile(temp_file, \'r\') as temp_file_object:\n        with tf.io.gfile.GFile(filename, \'w\') as file_object:\n            for line in temp_file_object:\n                line = line.strip()\n                line = line.replace(\', \', \',\')\n                if not line or \',\' not in line:\n                    continue\n                if line[-1] == \'.\':\n                    line = line[:-1]\n                line += \'\\n\'\n                file_object.write(line)\n    tf.io.gfile.remove(temp_file)\n\n\ndef download(data_dir):\n    """Downloads census data if it is not already present.\n\n    Args:\n      data_dir: directory where we will access/save the census data\n    """\n    tf.io.gfile.makedirs(data_dir)\n\n    training_file_path = os.path.join(data_dir, TRAINING_FILE)\n    if not tf.io.gfile.exists(training_file_path):\n        _download_and_clean_file(training_file_path, TRAINING_URL)\n\n    eval_file_path = os.path.join(data_dir, EVAL_FILE)\n    if not tf.io.gfile.exists(eval_file_path):\n        _download_and_clean_file(eval_file_path, EVAL_URL)\n\n    return training_file_path, eval_file_path\n\n\ndef preprocess(dataframe):\n    """Converts categorical features to numeric. Removes unused columns.\n\n    Args:\n      dataframe: Pandas dataframe with raw data\n\n    Returns:\n      Dataframe with preprocessed data\n    """\n    dataframe = dataframe.drop(columns=UNUSED_COLUMNS)\n\n    # Convert integer valued (numeric) columns to floating point\n    numeric_columns = dataframe.select_dtypes([\'int64\']).columns\n    dataframe[numeric_columns] = dataframe[numeric_columns].astype(\'float32\')\n\n    # Convert categorical columns to numeric\n    cat_columns = dataframe.select_dtypes([\'object\']).columns\n    dataframe[cat_columns] = dataframe[cat_columns].apply(lambda x: x.astype(\n        _CATEGORICAL_TYPES[x.name]))\n    dataframe[cat_columns] = dataframe[cat_columns].apply(lambda x: x.cat.codes)\n    return dataframe\n\n\ndef standardize(dataframe):\n    """Scales numerical columns using their means and standard deviation to get\n    z-scores: the mean of each numerical column becomes 0, and the standard\n    deviation becomes 1. This can help the model converge during training.\n\n    Args:\n      dataframe: Pandas dataframe\n\n    Returns:\n      Input dataframe with the numerical columns scaled to z-scores\n    """\n    dtypes = list(zip(dataframe.dtypes.index, map(str, dataframe.dtypes)))\n    # Normalize numeric columns.\n    for column, dtype in dtypes:\n        if dtype == \'float32\':\n            dataframe[column] -= dataframe[column].mean()\n            dataframe[column] /= dataframe[column].std()\n    return dataframe\n\n\ndef load_data():\n    """Loads data into preprocessed (train_x, train_y, eval_y, eval_y)\n    dataframes.\n\n    Returns:\n      A tuple (train_x, train_y, eval_x, eval_y), where train_x and eval_x are\n      Pandas dataframes with features for training and train_y and eval_y are\n      numpy arrays with the corresponding labels.\n    """\n    # Download Census dataset: Training and eval csv files.\n    training_file_path, eval_file_path = download(DATA_DIR)\n\n    # This census data uses the value \'?\' for missing entries. We use\n    # na_values to\n    # find ? and set it to NaN.\n    # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv\n    # .html\n    train_df = pd.read_csv(training_file_path, names=_CSV_COLUMNS,\n                           na_values=\'?\')\n    eval_df = pd.read_csv(eval_file_path, names=_CSV_COLUMNS, na_values=\'?\')\n\n    train_df = preprocess(train_df)\n    eval_df = preprocess(eval_df)\n\n    # Split train and eval data with labels. The pop method copies and removes\n    # the label column from the dataframe.\n    train_x, train_y = train_df, train_df.pop(_LABEL_COLUMN)\n    eval_x, eval_y = eval_df, eval_df.pop(_LABEL_COLUMN)\n\n    # Join train_x and eval_x to normalize on overall means and standard\n    # deviations. Then separate them again.\n    all_x = pd.concat([train_x, eval_x], keys=[\'train\', \'eval\'])\n    all_x = standardize(all_x)\n    train_x, eval_x = all_x.xs(\'train\'), all_x.xs(\'eval\')\n\n    # Reshape label columns for use with tf.data.Dataset\n    train_y = np.asarray(train_y).astype(\'float32\').reshape((-1, 1))\n    eval_y = np.asarray(eval_y).astype(\'float32\').reshape((-1, 1))\n\n    return train_x, train_y, eval_x, eval_y')


# The second file, called model.py, defines the input function and the model architecture. In this example, we use tf.data API for the data pipeline and create the model using the Keras Sequential API. We define a DNN with an input layer and 3 additonal layers using the Relu activation function. Since the task is a binary classification, the output layer uses the sigmoid activation.

# In[7]:


get_ipython().run_cell_magic('writefile', 'trainer/model.py', 'from __future__ import absolute_import\nfrom __future__ import division\nfrom __future__ import print_function\n\nimport tensorflow as tf\n\n\ndef input_fn(features, labels, shuffle, num_epochs, batch_size):\n    """Generates an input function to be used for model training.\n\n    Args:\n      features: numpy array of features used for training or inference\n      labels: numpy array of labels for each example\n      shuffle: boolean for whether to shuffle the data or not (set True for\n        training, False for evaluation)\n      num_epochs: number of epochs to provide the data for\n      batch_size: batch size for training\n\n    Returns:\n      A tf.data.Dataset that can provide data to the Keras model for training or\n        evaluation\n    """\n    if labels is None:\n        inputs = features\n    else:\n        inputs = (features, labels)\n    dataset = tf.data.Dataset.from_tensor_slices(inputs)\n\n    if shuffle:\n        dataset = dataset.shuffle(buffer_size=len(features))\n\n    # We call repeat after shuffling, rather than before, to prevent separate\n    # epochs from blending together.\n    dataset = dataset.repeat(num_epochs)\n    dataset = dataset.batch(batch_size)\n    return dataset\n\n\ndef create_keras_model(input_dim, learning_rate):\n    """Creates Keras Model for Binary Classification.\n\n    The single output node + Sigmoid activation makes this a Logistic\n    Regression.\n\n    Args:\n      input_dim: How many features the input has\n      learning_rate: Learning rate for training\n\n    Returns:\n      The compiled Keras model (still needs to be trained)\n    """\n    Dense = tf.keras.layers.Dense\n    model = tf.keras.Sequential(\n        [\n            Dense(100, activation=tf.nn.relu, kernel_initializer=\'uniform\',\n                  input_shape=(input_dim,)),\n            Dense(75, activation=tf.nn.relu),\n            Dense(50, activation=tf.nn.relu),\n            Dense(25, activation=tf.nn.relu),\n            Dense(1, activation=tf.nn.sigmoid)\n        ])\n\n    # Custom Optimizer:\n    # https://www.tensorflow.org/api_docs/python/tf/train/RMSPropOptimizer\n    optimizer = tf.keras.optimizers.RMSprop(lr=learning_rate)\n\n    # Compile Keras model\n    model.compile(\n        loss=\'binary_crossentropy\', optimizer=optimizer, metrics=[\'accuracy\'])\n    return model')


# The last file, called task.py, trains on data loaded and preprocessed in util.py. Using the tf.distribute.MirroredStrategy() scope, it is possible to train on a distributed fashion. The trained model is then saved in a TensorFlow SavedModel format.

# In[8]:


get_ipython().run_cell_magic('writefile', 'trainer/task.py', 'from __future__ import absolute_import\nfrom __future__ import division\nfrom __future__ import print_function\n\nimport argparse\nimport os\n\nfrom . import model\nfrom . import util\n\nimport tensorflow as tf\n\n\ndef get_args():\n    """Argument parser.\n\n    Returns:\n      Dictionary of arguments.\n    """\n    parser = argparse.ArgumentParser()\n    parser.add_argument(\n        \'--job-dir\',\n        type=str,\n        required=True,\n        help=\'local or GCS location for writing checkpoints and exporting \'\n             \'models\')\n    parser.add_argument(\n        \'--num-epochs\',\n        type=int,\n        default=20,\n        help=\'number of times to go through the data, default=20\')\n    parser.add_argument(\n        \'--batch-size\',\n        default=128,\n        type=int,\n        help=\'number of records to read during each training step, default=128\')\n    parser.add_argument(\n        \'--learning-rate\',\n        default=.01,\n        type=float,\n        help=\'learning rate for gradient descent, default=.01\')\n    parser.add_argument(\n        \'--verbosity\',\n        choices=[\'DEBUG\', \'ERROR\', \'FATAL\', \'INFO\', \'WARN\'],\n        default=\'INFO\')\n    args, _ = parser.parse_known_args()\n    return args\n\n\ndef train_and_evaluate(args):\n    """Trains and evaluates the Keras model.\n\n    Uses the Keras model defined in model.py and trains on data loaded and\n    preprocessed in util.py. Saves the trained model in TensorFlow SavedModel\n    format to the path defined in part by the --job-dir argument.\n\n    Args:\n      args: dictionary of arguments - see get_args() for details\n    """\n\n    train_x, train_y, eval_x, eval_y = util.load_data()\n\n    # dimensions\n    num_train_examples, input_dim = train_x.shape\n    num_eval_examples = eval_x.shape[0]\n\n    # Create the Keras Model\n    keras_model = model.create_keras_model(\n        input_dim=input_dim, learning_rate=args.learning_rate)\n\n    # Pass a numpy array by passing DataFrame.values\n    training_dataset = model.input_fn(\n        features=train_x.values,\n        labels=train_y,\n        shuffle=True,\n        num_epochs=args.num_epochs,\n        batch_size=args.batch_size)\n\n    # Pass a numpy array by passing DataFrame.values\n    validation_dataset = model.input_fn(\n        features=eval_x.values,\n        labels=eval_y,\n        shuffle=False,\n        num_epochs=args.num_epochs,\n        batch_size=num_eval_examples)\n\n    # Setup Learning Rate decay.\n    lr_decay_cb = tf.keras.callbacks.LearningRateScheduler(\n        lambda epoch: args.learning_rate + 0.02 * (0.5 ** (1 + epoch)),\n        verbose=True)\n\n    # Setup TensorBoard callback.\n    tensorboard_cb = tf.keras.callbacks.TensorBoard(\n        os.path.join(args.job_dir, \'keras_tensorboard\'),\n        histogram_freq=1)\n\n    # Train model\n    keras_model.fit(\n        training_dataset,\n        steps_per_epoch=int(num_train_examples / args.batch_size),\n        epochs=args.num_epochs,\n        validation_data=validation_dataset,\n        validation_steps=1,\n        verbose=1,\n        callbacks=[lr_decay_cb, tensorboard_cb])\n\n    export_path = os.path.join(args.job_dir, \'keras_export\')\n    tf.keras.models.save_model(keras_model, export_path)\n    print(\'Model exported to: {}\'.format(export_path))\n\n\n\nif __name__ == \'__main__\':\n    strategy = tf.distribute.MirroredStrategy()\n    with strategy.scope():\n        args = get_args()\n        tf.compat.v1.logging.set_verbosity(args.verbosity)\n        train_and_evaluate(args)')


# #### Step 2.2: Run a training job locally using the Python training program
# 
# **NOTE** When you run the same training job on AI Platform later in the lab, you'll see that the command is not much different from the above.
# 
# Specify an output directory and set a MODEL_DIR variable to hold the trained model, then run the training job locally by running the following command (by default, verbose logging is turned off. You can enable it by setting the --verbosity tag to DEBUG):

# In[9]:


get_ipython().run_cell_magic('bash', '', '\nMODEL_DIR=output\ngcloud ai-platform local train \\\n    --module-name trainer.task \\\n    --package-path trainer/ \\\n    --job-dir $MODEL_DIR \\\n    -- \\\n    --train-files $TRAIN_DATA \\\n    --eval-files $EVAL_DATA \\\n    --train-steps 1000 \\\n    --eval-steps 100')


# Check if the output has been written to the output folder:

# In[10]:


get_ipython().run_cell_magic('bash', '', '\nls output/keras_export/')


# #### Step 2.3: Prepare input for prediction
# 
# To receive valid and useful predictions, you must preprocess input for prediction in the same way that training data was preprocessed. In a production system, you may want to create a preprocessing pipeline that can be used identically at training time and prediction time.
# 
# For this exercise, use the training package's data-loading code to select a random sample from the evaluation data. This data is in the form that was used to evaluate accuracy after each epoch of training, so it can be used to send test predictions without further preprocessing.
# 

# Run the following snippet of code to preprocess the raw data from the adult.test.csv file. Here, we are grabbing 5 examples to run predictions on:

# In[11]:


from trainer import util
_, _, eval_x, eval_y = util.load_data()

prediction_input = eval_x.sample(5)
prediction_targets = eval_y[prediction_input.index]


# Check the numerical representation of the features by printing the preprocessed data:

# In[12]:


print(prediction_input)


# Notice that categorical fields, like occupation, have already been converted to integers (with the same mapping that was used for training). Numerical fields, like age, have been scaled to a z-score. Some fields have been dropped from the original data.
# 
# Export the prediction input to a newline-delimited JSON file:

# In[13]:


import json

with open('test.json', 'w') as json_file:
  for row in prediction_input.values.tolist():
    json.dump(row, json_file)
    json_file.write('\n')


# Inspect the .json file:

# In[14]:


get_ipython().run_cell_magic('bash', '', '\ncat test.json')


# #### Step 2.4: Use your trained model for prediction
# 
# Once you've trained your TensorFlow model, you can use it for prediction on new data. In this case, you've trained a census model to predict income category given some information about a person.
# 
# Run the following command to run prediction on the test.json file we created above:

# **Note:** If you get a "Bad magic number in .pyc file" error, go to the terminal and run:
# > cd ../../usr/lib/google-cloud-sdk/lib/googlecloudsdk/command_lib/ml_engine/
# 
# > sudo rm *.pyc

# In[15]:


get_ipython().run_cell_magic('bash', '', '\ngcloud ai-platform local predict \\\n    --model-dir output/keras_export/ \\\n    --json-instances ./test.json')


# Since the model's last layer uses a sigmoid function for its activation, outputs between 0 and 0.5 represent negative predictions **("<=50K")** and outputs between 0.5 and 1 represent positive ones **(">50K")**.

# ### Step 3: Run your training job in the cloud
# 
# Now that you've validated your model by running it locally, you will now get practice training using Cloud AI Platform.
# 
# **Note:** The initial job request will take several minutes to start, but subsequent jobs run more quickly. This enables quick iteration as you develop and validate your training job.
# 
# First, set the following variables:
# 

# In[16]:


get_ipython().run_cell_magic('bash', '', 'export PROJECT=$(gcloud config list project --format "value(core.project)")\necho "Your current GCP Project Name is: "${PROJECT}')


# In[22]:


PROJECT = "qwiklabs-gcp-04-1e5e10b85531"  # Replace with your project name
BUCKET_NAME=PROJECT+"-aiplatform"
REGION="us-central1"


# In[23]:


os.environ["PROJECT"] = PROJECT
os.environ["BUCKET_NAME"] = BUCKET_NAME
os.environ["REGION"] = REGION
os.environ["TFVERSION"] = "2.1"
os.environ["PYTHONVERSION"] = "3.7"


# #### Step 3.1: Set up a Cloud Storage bucket
# 
# The AI Platform services need to access Cloud Storage (GCS) to read and write data during model training and batch prediction.
# 
# Create a bucket using BUCKET_NAME as the name for the bucket and copy the data into it.

# In[24]:


get_ipython().run_cell_magic('bash', '', '\nif ! gsutil ls | grep -q gs://${BUCKET_NAME}; then\n    gsutil mb -l ${REGION} gs://${BUCKET_NAME}\nfi\ngsutil cp -r data gs://$BUCKET_NAME/data')


# Set the TRAIN_DATA and EVAL_DATA variables to point to the files:

# In[25]:


get_ipython().run_cell_magic('bash', '', '\nexport TRAIN_DATA=gs://$BUCKET_NAME/data/adult.data.csv\nexport EVAL_DATA=gs://$BUCKET_NAME/data/adult.test.csv')


# Use gsutil again to copy the JSON test file test.json to your Cloud Storage bucket:

# In[26]:


get_ipython().run_cell_magic('bash', '', '\ngsutil cp test.json gs://$BUCKET_NAME/data/test.json')


# Set the TEST_JSON variable to point to that file:

# In[27]:


get_ipython().run_cell_magic('bash', '', '\nexport TEST_JSON=gs://$BUCKET_NAME/data/test.json')


# **Go back to the lab instructions and check your progress by testing the completed tasks:**
# 
# **- "Set up a Google Cloud Storage".**
# 
# **- "Upload the data files to your Cloud Storage bucket".**

# #### Step 3.2: Run a single-instance trainer in the cloud
# 
# With a validated training job that runs in both single-instance and distributed mode, you're now ready to run a training job in the cloud. For this example, we will be requesting a single-instance training job.
# 
# Use the default BASIC scale tier to run a single-instance training job. The initial job request can take a few minutes to start, but subsequent jobs run more quickly. This enables quick iteration as you develop and validate your training job.
# 
# Select a name for the initial training run that distinguishes it from any subsequent training runs. For example, we can use date and time to compose the job id.
# 
# Specify a directory for output generated by AI Platform by setting an OUTPUT_PATH variable to include when requesting training and prediction jobs. The OUTPUT_PATH represents the fully qualified Cloud Storage location for model checkpoints, summaries, and exports. You can use the BUCKET_NAME variable you defined in a previous step. It's a good practice to use the job name as the output directory.
# 
# Run the following command to submit a training job in the cloud that uses a single process. This time, set the --verbosity tag to DEBUG so that you can inspect the full logging output and retrieve accuracy, loss, and other metrics. The output also contains a number of other warning messages that you can ignore for the purposes of this sample:

# In[34]:


get_ipython().run_cell_magic('bash', '', '\nJOB_ID=census_$(date -u +%y%m%d_%H%M%S)\nOUTPUT_PATH=gs://$BUCKET_NAME/$JOB_ID\ngcloud ai-platform jobs submit training $JOB_ID \\\n    --job-dir $OUTPUT_PATH \\\n    --runtime-version $TFVERSION \\\n    --python-version $PYTHONVERSION \\\n    --module-name trainer.task \\\n    --package-path trainer/ \\\n    --region $REGION \\\n    -- \\\n    --train-files $TRAIN_DATA \\\n    --eval-files $EVAL_DATA \\\n    --train-steps 1000 \\\n    --eval-steps 100 \\\n    --verbosity DEBUG')


# Set an environment variable with the jobId generated above:

# In[39]:


os.environ["JOB_ID"] = "census_210821_201659" # Replace with your job id


# You can monitor the progress of your training job by watching the logs on the command line by running:
# 
# `gcloud ai-platform jobs stream-logs $JOB_ID`
# 
# Or monitor it in the Console at `AI Platform > Jobs`. Wait until your AI Platform training job is done. It is finished when you see a green check mark by the jobname in the Cloud Console, or when you see the message Job completed successfully from the Cloud Shell command line.

# **Go back to the lab instructions and check your progress by testing the completed task:**
# 
# **- "Run a single-instance trainer in the cloud".**
# 

# #### Step 3.3: Deploy your model to support prediction
# 
# By deploying your trained model to AI Platform to serve online prediction requests, you get the benefit of scalable serving. This is useful if you expect your trained model to be hit with many prediction requests in a short period of time.
# 
# 
# Create an AI Platform model:

# In[42]:


os.environ["MODEL_NAME"] = "census_20210821"


# In[43]:


get_ipython().run_cell_magic('bash', '', '\ngcloud ai-platform models create $MODEL_NAME --regions=$REGION')


# Set the environment variable MODEL_BINARIES to the full path of your exported trained model binaries `$OUTPUT_PATH/keras_export/`.

# You'll deploy this trained model.
# 
# Run the following command to create a version v1 of your model:

# In[44]:


get_ipython().run_cell_magic('bash', '', '\nOUTPUT_PATH=gs://$BUCKET_NAME/$JOB_ID\nMODEL_BINARIES=$OUTPUT_PATH/keras_export/\ngcloud ai-platform versions create v1 \\\n--model $MODEL_NAME \\\n--origin $MODEL_BINARIES \\\n--runtime-version $TFVERSION \\\n--python-version $PYTHONVERSION \\\n--region=global')


# It may take several minutes to deploy your trained model. When done, you can see a list of your models using the models list command:

# In[45]:


get_ipython().run_cell_magic('bash', '', '\ngcloud ai-platform models list')


# **Go back to the lab instructions and check your progress by testing the completed tasks:**
# 
# **- "Create an AI Platform model".**
# 
# **- "Create a version v1 of your model".**

# #### Step 3.4: Send an online prediction request to your deployed model
# 
# You can now send prediction requests to your deployed model. The following command sends a prediction request using the test.json.
# 
# The response includes the probabilities of each label **(>50K and <=50K)** based on the data entry in test.json, thus indicating whether the predicted income is greater than or less than 50,000 dollars.

# In[46]:


get_ipython().run_cell_magic('bash', '', '\ngcloud ai-platform predict \\\n--model $MODEL_NAME \\\n--version v1 \\\n--json-instances ./test.json \\\n--region global')


# **Note:** AI Platform supports batch prediction, too, but it's not included in this lab. See the documentation for more info.

# **Go back to the lab instructions to answer some multiple choice questions to reinforce your uncerstanding of some of these lab's concepts.**

# ### Congratulations!
# 
# In this lab you've learned how to train a TensorFlow model both locally and on AI Platform, how to prepare data for prediction and to perform predictions both locally and in the Cloud AI Platform.
