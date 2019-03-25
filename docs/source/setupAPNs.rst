############################################
Setup APNs (Apple Push Notification service)
############################################

login your apple developer account

- Go to **Certificates, Identifiers & Profiles**
- Click **Keys**
- Click **+** button

.. image:: images/key_1.png

- Enter **Name**
- Check **Appl  Push Notification service**
- Click **Continue** button

.. image:: images/key_2.png

- Click **Confirm** button

.. image:: images/key_3.png

- Record your **Key ID**. It will be need for config.json file later.
- Click **Download** button. 
  The .p8 file will be used for config.json file later.

.. image:: images/key_4.png

- Go to **Account**
- Select **Membership**
- Record  your **Team ID**. It will be need for config.json file later.

.. image:: images/key_5.png

- Go to **Certificates, Identifiers & Profiles**
- Select **App ID**
- Record the **ID** for your APNs project.
  App ID will be used for config.json file later.

.. image:: images/key_6.png

- Also, check if **Push Notification** is enable.

.. image:: images/key_7.png
