Discord CipherChat
==================

The CipherChat program offers users a customizable, secure, and anonymous chatroom-based messaging service.

Currently, it is configured to utilize Discord's API as its server since it is easy and free to set up.


What you need:
--------------
To start using CipherChat, there are several pieces of data you need first.

These can all be inserted into the "config" YAML files, and later cached as custom profiles using the "config" utility tool.

You need:
- Your personal Discord OAuth token (to easily fetch data from Discord without the need for a bot)
- At least 1 webhook that your clients can use to send messages
  [additional webhooks will increase scalability but decrease speed, so one webhook per profile is recommended]
- The channel(s) associated with the webhook(s)
- An self-ID tag (it can be whatever you want!)


What does it do?:
-----------------
When you create a new channel, it contains its own unique AES key, and this key can be securely shared by anyone with channel access.

When you send a message, anyone with access to the channel will be able to see who sent it (your self-ID, the contents, and any attachment links*)


Cryptography:
-------------
CipherChat's cryptography library uses AES-256 for messaging and local encryption and RSA-4096 for key exchange.

These protocols are industry standards and offer (virtually) complete confidentiality.


Benefits and drawbacks:
-----------------------
CipherChat values confidentiality and anonymity above all else.

Because self-ID values are chosen by you, and all data is sent via anonymous webhook (and can be sent behind a VPN), all messages within a chatroom are not linked to any accounts or personal data.

This is one of the most important goals that I set out to achieve with this software... however, it also means that no user authentication is available.

So make sure that channel keys are ONLY shared with people you trust!


The "chatroom" model:
---------------------
Since each API "server" is set up separately for different CipherChat clients, data only needs to be routed for a small number of people compared to larger services.

When you log into CipherChat, ALL Discord channel data is fetched using your OAuth token, and data from the channel you want to see is filtered on the client-side.
[ note: this does not apply to different profiles using separate webhooks and channels ]

This ensures that Discord user data cannot be utilized to determine which channels a person is a member of, as all available data is fetched on startup no matter what.

Furthermore, anyone with access to your service webhook can theoretically send data and no identifying information is collected from webhook requests.

And anyone with read access to your service channels can also theoretically make requests to the data (and they will every time said channel is opened).
[ though keep in mind that this will only increase anonymity on servers with higher volumes of people ]

So overall, this model distances "you" from "your messages" and makes it much easier to stay anonymous, even if (somehow) confidentiality is compromised.


Safety in numbers:
------------------
The more people who have read access to service channels and theoretical access to service webhooks, the less likely it is to ascertain who is part of what channel.
[ technically it is practically impossible either way to know for certain who sent webhook data, but smaller servers (and as such fewer people with read access to channels) makes narrowing down likely culprits much easier ]

As with anything, the fewer people there are, the harder it is to stay anonymous.  But even without larger groups, CipherChat should still offer reasonable doubt about the IDs of message senders.

And by using profiles, a large server of people can have hundreds of different channels each serving a small group of people... all increasing each others' anonymity.

And so, I have included a CipherChat "community" Discord server below, where I hope to start building this secure community!  Feel free to join today!
[ https://discord.gg/uDSdHFGV83 ]


Deleting channels:
------------------
When a channel is deleted on your local device, all channel data -- including the associated AES key -- will be removed.

If everyone in the channel deletes it locally, all channel data will become unrecoverable.


Attachments:
------------
Users can also attach files to their CipherChat messages, and in the consoles these attachments will appear as a unique "attachment link."

To securely extract and decrypt the associated file, use the "attachment" utility and paste the link for the file you want to download.


Conclusion:
-----------
TL;DR: CipherChat's security and anonymity features are pretty cool ig

Do you like privacy, security, and anonymity?  Want to chat about building your meth empire without your pesky brother-in-law DEA agent finding out?

Then Discord CipherChat might just be the solution for you!

Feel free to join the CipherChat community Discord:
[ https://discord.gg/uDSdHFGV83 ]


[DISCLAIMER]
Don't use this service to discuss or promote any illegal activity... blah blah... I'm not responsible for any dumb trouble you get yourself in... blah blah
(just because your messages are secure doesn't mean the IRS won't still find out that you committed massive amounts of tax fraud, Ted)