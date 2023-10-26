import {FeeDeductions} from './feeCalculator';
import {Constants} from "./constants";

function updateOutput() {
    const priceInput = document.getElementById('priceInput') as HTMLInputElement;
    const togglePriceMode = document.getElementById('togglePriceMode') as HTMLInputElement;

    let price = parseFloat(priceInput.value) || 0;

    // Calculate ask price if listing price mode is enabled
    if (togglePriceMode.checked) {
        price = Math.round(price / (1 + Constants.BUYER_FEE_RATE));
    }

    const shippingCostInput = document.getElementById('shippingCost') as HTMLInputElement;
    const salesTaxInput = document.getElementById('salesTax') as HTMLInputElement;
    const featuredInput = document.getElementById('featured') as HTMLInputElement;

    const shippingCost = parseFloat(shippingCostInput.value) || 0;
    const salesTax = parseFloat(salesTaxInput.value) || 0;
    const featured = featuredInput.checked;

    const feeObj = new FeeDeductions(price, shippingCost, salesTax, featured);

    document.getElementById('buyerPaid')!.innerText = `$${feeObj.buyer_paid.toFixed(2)}`;

    document.getElementById('listingPrice')!.innerText = `$${feeObj.listing_price.toFixed(2)}`;
    document.getElementById('listingPriceDiff')!.innerText = `(-$${(feeObj.buyer_paid - feeObj.listing_price).toFixed(2)} sales tax @ ${salesTax.toFixed(2)}%)`;

    document.getElementById('askPriceOutput')!.innerText = `$${feeObj.ask_price.toFixed(2)}`;
    document.getElementById('askPriceDiff')!.innerText = `(-$${feeObj.buyer_fee.toFixed(2)} buyer fee @ ${(Constants.BUYER_FEE_RATE * 100).toFixed(2)}%)`;

    document.getElementById('swappaPayout')!.innerText = `$${(feeObj.ask_price - feeObj.seller_fee).toFixed(2)}`;
    document.getElementById('swappaPayoutDiff')!.innerText = `(-$${feeObj.seller_fee.toFixed(2)} seller fee @ ${(Constants.SELLER_FEE_RATE * 100).toFixed(2)}%)`;

    document.getElementById('afterPaypal')!.innerText = `$${feeObj.afterPaypal().toFixed(2)}`;
    document.getElementById('afterPaypalDiff')!.innerText = `(-$${feeObj.paypal_fee.toFixed(2)} PayPal fee @ ${(Constants.PAYPAL_FEE_RATE * 100).toFixed(2)}% + $${Constants.PAYPAL_FIXED_FEE.toFixed(2)})`;

    document.getElementById('afterShipping')!.innerText = `$${feeObj.afterShipping().toFixed(2)}`;
    document.getElementById('afterShippingDiff')!.innerText = shippingCost > 0 ? `(-$${shippingCost.toFixed(2)} shipping)` : '(shipping ignored)';

    document.getElementById('finalRevenue')!.innerText = `$${feeObj.finalRevenue().toFixed(2)}`;
    document.getElementById('finalRevenueDiff')!.innerText = featured ? `(-$${Constants.BOOST_FEE.toFixed(2)} featured listing fee)` : '';

    let totalFees = (feeObj.buyer_fee + feeObj.seller_fee + feeObj.paypal_fee + shippingCost + (featured ? Constants.BOOST_FEE : 0));
    document.getElementById('totalFees')!.innerText = `$${totalFees.toFixed(2)}`;
    document.getElementById('totalFeesDiff')!.innerText = `(${(totalFees / feeObj.listing_price * 100).toFixed(2)}% of listing price)`;
}

function updateInputLabel() {
    const togglePriceMode = document.getElementById('togglePriceMode') as HTMLInputElement;
    const priceLabel = document.getElementById('priceLabel') as HTMLLabelElement;

    if (togglePriceMode.checked) {
        priceLabel.innerText = "Listing Price";
    } else {
        priceLabel.innerText = "Ask Price";
    }
}

// Add event listeners
(document.getElementById('priceInput') as HTMLInputElement).addEventListener('input', updateOutput);
(document.getElementById('shippingCost') as HTMLInputElement).addEventListener('input', updateOutput);
(document.getElementById('salesTax') as HTMLInputElement).addEventListener('input', updateOutput);
(document.getElementById('featured') as HTMLInputElement).addEventListener('change', updateOutput);
(document.getElementById('togglePriceMode') as HTMLInputElement).addEventListener('change', () => {
    updateInputLabel();
    updateOutput();
});

// Initial setup
updateInputLabel();
updateOutput();
