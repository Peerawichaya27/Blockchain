const RSAVerification = artifacts.require("RSAVerification");

module.exports = function (deployer) {
  deployer.deploy(RSAVerification);
};
